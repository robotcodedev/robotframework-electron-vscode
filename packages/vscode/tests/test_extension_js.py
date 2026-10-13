"""Runs the helper extension with Node and a fake `vscode` module."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

import VSCode

EXTENSION_JS = Path(VSCode.__file__).with_name("extension") / "extension.js"

HARNESS = """
const Module = require('module');
const fs = require('fs');
const path = require('path');
const [extensionPath, scenario, storage] = process.argv.slice(2);

// The workspace of the window, as the extension host would see it, by scenario.
const folder = (fsPath) => ({ uri: { fsPath } });
const workspaces = {
    folder: { folders: [folder('/work/a')], storageUri: '/user/workspaceStorage/folder-id/ext' },
    'multi-root': {
        file: { scheme: 'file', fsPath: '/work/all.code-workspace' },
        folders: [folder('/work/a'), folder('/work/b')],
        storageUri: '/user/workspaceStorage/multi-root-id/ext',
    },
    untitled: {
        file: { scheme: 'untitled', fsPath: '1791844322053' },
        folders: [folder('/work/a')],
        storageUri: '/user/workspaceStorage/untitled-id/ext',
    },
    empty: {},
};
const workspace = workspaces[scenario];
const vscode = {
    version: '1.141.0',
    workspace: { workspaceFile: workspace.file, workspaceFolders: workspace.folders },
};
const load = Module._load;
Module._load = function (request, ...rest) {
    return request === 'vscode' ? vscode : load.call(this, request, ...rest);
};
const extension = require(extensionPath);
const context = {
    extension: { packageJSON: { version: '0.2.0-dev.12' } },
    globalStorageUri: { fsPath: storage },
    storageUri: workspace.storageUri && { fsPath: workspace.storageUri },
};

(async () => {
    await extension.activate(context);
    const hosts = path.join(storage, 'hosts');
    const files = fs.readdirSync(hosts);
    const endpoint = JSON.parse(fs.readFileSync(path.join(hosts, files[0]), 'utf8'));
    async function call(method, script, token = endpoint.token) {
        const response = await fetch(`http://127.0.0.1:${endpoint.port}/`, {
            method,
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: method === 'POST' ? JSON.stringify({ script, arg: { answer: 42 } }) : undefined,
        });
        return { status: response.status, body: await response.json() };
    }
    const outcome = {
        files,
        endpoint: { ...endpoint, port: typeof endpoint.port, token: typeof endpoint.token },
        ownPid: endpoint.pid === process.pid,
        probe: await call('GET'),
        value: await call('POST', '(vscode, arg) => [vscode.version, arg.answer]'),
        undefined: await call('POST', '() => undefined'),
        function: await call('POST', '() => () => 1'),
        symbol: await call('POST', "() => Symbol('robot')"),
        promise: await call('POST', 'async (vscode) => vscode.version'),
        thrown: await call('POST', "() => { throw new Error('broken') }"),
        rejected: await call('POST', "() => Promise.reject(new Error('rejected'))"),
        notSerialisable: await call('POST', '() => 10n'),
        withoutToken: await call('POST', '() => { globalThis.ran = true }', null),
        wrongToken: await call('POST', '() => { globalThis.ran = true }', 'wrong'),
        probeWithoutToken: await call('GET', undefined, null),
    };
    outcome.ran = globalThis.ran === true;
    extension.deactivate();
    outcome.filesAfterDeactivation = fs.readdirSync(hosts);
    console.log(JSON.stringify(outcome));
    // Idle keep-alive connections of fetch would keep Node running for a while.
    process.exit(0);
})().catch((error) => {
    console.error(error);
    process.exit(1);
});
"""


@pytest.fixture(scope="module")
def outcomes(tmp_path_factory) -> dict[str, dict[str, Any]]:
    """Runs the extension once per workspace scenario."""
    folder = tmp_path_factory.mktemp("extension")
    harness = folder / "harness.js"
    harness.write_text(HARNESS)
    results = {}
    for scenario in ("folder", "multi-root", "untitled", "empty"):
        completed = subprocess.run(
            ["node", str(harness), str(EXTENSION_JS), scenario, str(folder / scenario)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        results[scenario] = json.loads(completed.stdout)
    return results


def test_runs_the_function_with_vscode_and_arg(outcomes):
    assert outcomes["folder"]["value"] == {"status": 200, "body": {"result": ["1.141.0", 42]}}


@pytest.mark.parametrize("case", ["undefined", "function", "symbol"])
def test_returns_null_for_values_without_json(outcomes, case):
    assert outcomes["folder"][case] == {"status": 200, "body": {"result": None}}


def test_waits_for_a_promise(outcomes):
    assert outcomes["folder"]["promise"]["body"] == {"result": "1.141.0"}


@pytest.mark.parametrize(("case", "message"), [("thrown", "broken"), ("rejected", "rejected")])
def test_answers_with_the_error_of_the_function(outcomes, case, message):
    answer = outcomes["folder"][case]

    assert answer["status"] == 200
    assert answer["body"]["error"]["message"] == message
    assert "Error: " + message in answer["body"]["error"]["stack"]


def test_answers_with_an_error_for_a_result_that_is_no_json(outcomes):
    message = outcomes["folder"]["notSerialisable"]["body"]["error"]["message"]

    assert message.startswith("The function's result cannot be serialised as JSON: ")


def test_answers_a_probe_with_its_process_id(outcomes):
    outcome = outcomes["folder"]

    assert outcome["probe"] == {"status": 200, "body": {"pid": outcome["endpoint"]["pid"]}}
    assert outcome["ownPid"]


@pytest.mark.parametrize("case", ["withoutToken", "wrongToken", "probeWithoutToken"])
def test_rejects_requests_without_the_token(outcomes, case):
    answer = outcomes["folder"][case]

    assert answer == {"status": 403, "body": {"error": {"message": "The request has no valid token."}}}
    assert not outcomes["folder"]["ran"]


@pytest.mark.parametrize(
    ("scenario", "workspace", "workspace_id"),
    [
        ("folder", "/work/a", "folder-id"),
        ("multi-root", "/work/all.code-workspace", "multi-root-id"),
        ("untitled", None, "untitled-id"),
        ("empty", None, None),
    ],
)
def test_writes_the_endpoint_with_the_workspace(outcomes, scenario, workspace, workspace_id):
    outcome = outcomes[scenario]

    assert outcome["files"] == [f"{outcome['endpoint']['pid']}.json"]
    assert outcome["endpoint"] == {
        "port": "number",
        "token": "string",
        "pid": outcome["endpoint"]["pid"],
        "version": "0.2.0-dev.12",
        "workspace": workspace,
        "workspaceId": workspace_id,
    }


def test_removes_the_endpoint_when_deactivated(outcomes):
    assert outcomes["folder"]["filesAfterDeactivation"] == []
