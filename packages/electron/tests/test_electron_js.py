"""Runs electron.js with Node and fakes for Playwright and Browser's adoptContext hook."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

import Electron

ELECTRON_JS = Path(Electron.__file__).with_name("electron.js")

HARNESS = """
const { robotframeworkElectronLaunch } = require(process.argv[2]);
const scenario = process.argv[3];
const calls = [];
const app = {
    firstWindow: async () => {
        calls.push('firstWindow');
        if (scenario === 'no-window') throw new Error('no window');
        return { video: () => null };
    },
    context: () => ({ setDefaultTimeout: (timeout) => calls.push(`setDefaultTimeout ${timeout}`) }),
    close: async () => {
        calls.push('close');
        if (scenario === 'close-fails') throw new Error('close failed');
    },
    process: () => ({ kill: () => calls.push('kill') }),
};
const playwright = {
    _electron: {
        launch: async () => {
            calls.push('launch');
            return app;
        },
    },
};
async function adoptContext() {
    calls.push('adoptContext');
    if (scenario === 'adopt-fails' || scenario === 'close-fails') throw new Error('adopt failed');
    return { browserId: 'browser', contextId: 'context', pageId: 'page' };
}
const hook = scenario === 'no-hook' ? 'RESERVED' : adoptContext;
robotframeworkElectronLaunch('/electron', [], {}, '/cwd', 1000, null, null, null, 7000, playwright, hook)
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls })));
"""


def run(tmp_path: Path, scenario: str) -> dict[str, Any]:
    harness = tmp_path / "harness.js"
    harness.write_text(HARNESS)
    completed = subprocess.run(
        ["node", str(harness), str(ELECTRON_JS), scenario], capture_output=True, text=True, check=True, timeout=30
    )
    outcome: dict[str, Any] = json.loads(completed.stdout)
    return outcome


def test_returns_the_adopted_context(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["result"] == {"browserId": "browser", "contextId": "context", "pageId": "page", "videoPath": None}
    assert outcome["calls"] == ["launch", "firstWindow", "setDefaultTimeout 7000", "adoptContext"]


def test_starts_nothing_without_the_hook(tmp_path):
    outcome = run(tmp_path, "no-hook")

    assert "no adoptContext hook" in outcome["error"]
    assert outcome["calls"] == []


@pytest.mark.parametrize(
    ("scenario", "error", "calls"),
    [
        ("no-window", "no window", ["launch", "firstWindow", "close"]),
        ("adopt-fails", "adopt failed", ["launch", "firstWindow", "setDefaultTimeout 7000", "adoptContext", "close"]),
        (
            "close-fails",
            "adopt failed",
            ["launch", "firstWindow", "setDefaultTimeout 7000", "adoptContext", "close", "kill"],
        ),
    ],
)
def test_closes_the_application_when_the_start_fails(tmp_path, scenario, error, calls):
    outcome = run(tmp_path, scenario)

    assert outcome["error"] == error
    assert outcome["calls"] == calls
