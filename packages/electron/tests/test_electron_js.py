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
const options = {};
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
        launch: async (launchOptions) => {
            calls.push('launch');
            options.launch = launchOptions;
            return app;
        },
    },
};
async function adoptContext(context, adoptOptions) {
    calls.push('adoptContext');
    options.adopt = adoptOptions.contextOptions;
    if (scenario === 'adopt-fails' || scenario === 'close-fails') throw new Error('adopt failed');
    return { browserId: 'browser', contextId: 'context', pageId: 'page' };
}
const hook = scenario === 'no-hook' ? 'RESERVED' : adoptContext;
const launchOptions = scenario === 'options' ? { colorScheme: 'dark', locale: 'de-DE', bypassCSP: true } : {};
robotframeworkElectronLaunch('/electron', [], {}, '/cwd', 1000, null, null, null, launchOptions, 7000, playwright, hook)
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls, options })));
"""


EVALUATE_HARNESS = """
const { robotframeworkElectronLaunch, robotframeworkElectronEvaluate } = require(process.argv[2]);
const scenario = process.argv[3];
const calls = [];
const context = { setDefaultTimeout: () => {} };
const electron = { app: { getName: () => 'fixture' } };
const app = {
    firstWindow: async () => ({ video: () => null }),
    context: () => context,
    browserWindow: async () => {
        calls.push('browserWindow');
        return { title: 'window of the page', dispose: async () => calls.push('dispose') };
    },
    // Playwright would turn the window handle into the BrowserWindow it points to.
    evaluate: async (pageFunction, arg) => pageFunction(electron, arg),
};
const playwright = { _electron: { launch: async () => app } };
let onClose;
async function adoptContext(adoptedContext, options) {
    onClose = options.onClose;
    return { browserId: 'browser=app', contextId: 'context', pageId: 'page' };
}
const page = scenario === 'other-page' ? { context: () => ({}) } : { context: () => context };
const script = '(electron, arg, window) => [electron.app.getName(), arg, window && window.title]';
(async () => {
    const launchArguments = ['/electron', [], {}, '/cwd', 1000, null, null, null, {}, 7000];
    await robotframeworkElectronLaunch(...launchArguments, playwright, adoptContext);
    if (scenario === 'closed') await onClose();
    const browserId = scenario === 'unknown' ? 'browser=other' : 'browser=app';
    return robotframeworkElectronEvaluate(browserId, script, 42, page);
})()
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls })));
"""


def run(tmp_path: Path, scenario: str, harness_code: str = HARNESS) -> dict[str, Any]:
    harness = tmp_path / "harness.js"
    harness.write_text(harness_code)
    completed = subprocess.run(
        ["node", str(harness), str(ELECTRON_JS), scenario], capture_output=True, text=True, check=True, timeout=30
    )
    outcome: dict[str, Any] = json.loads(completed.stdout)
    return outcome


def test_returns_the_adopted_context(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["result"] == {"browserId": "browser", "contextId": "context", "pageId": "page", "videoPath": None}
    assert outcome["calls"] == ["launch", "firstWindow", "setDefaultTimeout 7000", "adoptContext"]


def test_application_decides_the_color_scheme_by_default(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["options"]["launch"]["colorScheme"] is None
    assert outcome["options"]["adopt"] == {"acceptDownloads": True, "colorScheme": None}


def test_launch_options_reach_playwright_and_browser(tmp_path):
    outcome = run(tmp_path, "options")

    expected = {"acceptDownloads": True, "colorScheme": "dark", "locale": "de-DE", "bypassCSP": True}
    assert {key: outcome["options"]["launch"][key] for key in expected} == expected
    assert outcome["options"]["adopt"] == expected


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


def test_evaluates_with_the_window_of_the_applications_page(tmp_path):
    outcome = run(tmp_path, "own-page", EVALUATE_HARNESS)

    assert outcome["result"] == ["fixture", 42, "window of the page"]
    assert outcome["calls"] == ["browserWindow", "dispose"]


def test_evaluates_without_a_window_for_a_page_of_another_browser(tmp_path):
    outcome = run(tmp_path, "other-page", EVALUATE_HARNESS)

    assert outcome["result"] == ["fixture", 42, None]
    assert outcome["calls"] == []


@pytest.mark.parametrize(("scenario", "browser_id"), [("unknown", "browser=other"), ("closed", "browser=app")])
def test_evaluating_fails_for_a_browser_that_is_no_open_application(tmp_path, scenario, browser_id):
    outcome = run(tmp_path, scenario, EVALUATE_HARNESS)

    assert outcome["error"] == f"Browser '{browser_id}' is not an application started by 'New Electron Application'."
