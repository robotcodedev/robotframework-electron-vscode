"""Runs electron.js with Node and fakes for Playwright and Browser's adoptContext hook."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

import Electron

ELECTRON_JS = Path(Electron.__file__).with_name("electron.js")

FAKE_PAGES = """
// A fake main process with a window and a view inside it, and fake pages for both.
const windowContents = {};
const viewContents = {};
const contentsByTarget = { window: windowContents, view: viewContents };
const mainProcess = {
    webContents: { fromDevToolsTargetId: (targetId) => contentsByTarget[targetId] },
    BrowserWindow: { fromWebContents: () => ({ id: 1, webContents: windowContents }) },
};
const cdpSession = (page) => ({
    send: async () => ({ targetInfo: { targetId: page.name } }),
    detach: async () => {},
});
function fakePage(name, context, closed = false) {
    const video = { path: async () => `${name}.webm` };
    return { name, isClosed: () => closed, context: () => context, video: () => video };
}
"""

HARNESS = """
const { robotframeworkElectronLaunch } = require(process.argv[2]);
const scenario = process.argv[3];
const calls = [];
const options = {};
const context = { newCDPSession: async (page) => cdpSession(page) };
const windowPage = fakePage('window', context);
const viewPage = fakePage('view', context);
const app = {
    firstWindow: async () => {
        calls.push('firstWindow');
        if (scenario === 'no-window') throw new Error('no window');
        if (scenario === 'view-first') return viewPage;
        if (scenario === 'first-closed') return fakePage('closed', context, true);
        return windowPage;
    },
    windows: () => [viewPage, windowPage],
    context: () => context,
    evaluate: async (pageFunction, arg) => pageFunction(mainProcess, arg),
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
    options.activePage = adoptOptions.activePage?.name ?? null;
    if (scenario === 'adopt-fails' || scenario === 'close-fails') throw new Error('adopt failed');
    return { browserId: 'browser', contextId: 'context', pageId: 'page', videoPath: null };
}
const hook = scenario === 'no-hook' ? 'RESERVED' : adoptContext;
const launchOptions = scenario === 'options' ? { colorScheme: 'dark', locale: 'de-DE', bypassCSP: true } : {};
const recordVideo = scenario === 'view-first' || scenario === 'first-closed' ? {} : null;
const launchArguments = ['/electron', [], {}, '/cwd', 1000, recordVideo, null, null, '/traces', launchOptions];
robotframeworkElectronLaunch(...launchArguments, playwright, hook)
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls, options })));
"""


EVALUATE_HARNESS = """
const { robotframeworkElectronLaunch, robotframeworkElectronEvaluate } = require(process.argv[2]);
const scenario = process.argv[3];
const calls = [];
const context = { newCDPSession: async (page) => cdpSession(page) };
const electron = { ...mainProcess, app: { getName: () => 'fixture' } };
const windowPage = fakePage('window', context);
const app = {
    firstWindow: async () => windowPage,
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
    const launchArguments = ['/electron', [], {}, '/cwd', 1000, null, null, null, '/traces', {}];
    await robotframeworkElectronLaunch(...launchArguments, playwright, adoptContext);
    if (scenario === 'closed') await onClose();
    const browserId = scenario === 'unknown' ? 'browser=other' : 'browser=app';
    return robotframeworkElectronEvaluate(browserId, script, 42, page);
})()
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls })));
"""


WINDOWS_HARNESS = """
const electronJs = require(process.argv[2]);
const scenario = process.argv[3];
const calls = [];
const context = { newCDPSession: async (page) => cdpSession(page) };
// Without a window manager, maximize() and minimize() change nothing.
const ignored = scenario === 'maximize-ignored';
// The content size that a window gets differs by a pixel from the one it was asked for.
const offByOne = scenario === 'size-fractional' || scenario === 'size-off';
// A fake BrowserWindow with web contents of its own, which does what it is asked, as under a window manager.
function fakeWindow(id, title) {
    const window = {
        id,
        title,
        maximized: false,
        minimized: false,
        fullScreen: false,
        wasMaximized: false,
        // How many reads of isMaximized() until the window manager maximises the window again.
        maximizedAfterReads: 0,
        // How many size requests the window manager resets to the size from before.
        resets: scenario === 'size-reset' ? 1 : 0,
        size: [800, 600],
        getTitle: () => window.title,
        isMaximized: () => {
            if (window.maximizedAfterReads > 0 && --window.maximizedAfterReads === 0) window.maximized = true;
            return window.maximized;
        },
        isMinimized: () => window.minimized,
        isFullScreen: () => window.fullScreen,
        maximize: () => {
            calls.push(`maximize ${id}`);
            if (!ignored) Object.assign(window, { maximized: true, minimized: false });
        },
        minimize: () => {
            calls.push(`minimize ${id}`);
            if (!ignored) Object.assign(window, { wasMaximized: window.maximized, maximized: false, minimized: true });
        },
        restore: () => {
            calls.push(`restore ${id}`);
            // A minimised window comes back in its previous state, here on its way through normal.
            const throughNormal = scenario === 'restore-transient' && window.wasMaximized;
            Object.assign(window, { maximized: window.wasMaximized && !throughNormal, minimized: false });
            if (throughNormal) window.maximizedAfterReads = 2;
        },
        unmaximize: () => {
            calls.push(`unmaximize ${id}`);
            window.maximized = false;
        },
        setFullScreen: (fullScreen) => {
            calls.push(`setFullScreen ${id} ${fullScreen}`);
            window.fullScreen = fullScreen;
        },
        getContentSize: () => window.size,
        setContentSize: (width, height) => {
            calls.push(`setContentSize ${id}`);
            if (window.resets > 0) window.resets -= 1;
            else window.size = offByOne ? [width - 1, height + 1] : [width, height];
        },
        getBounds: () => ({ x: 0, y: 0, width: 800, height: 600 }),
        webContents: {},
    };
    return window;
}
// Electron lists its windows in no particular order.
const windows = [fakeWindow(2, 'Second'), fakeWindow(1, 'First')];
if (scenario === 'find-twice') windows.push(fakeWindow(3, 'Second'));
if (scenario === 'find-late') setTimeout(() => windows.push(fakeWindow(3, 'Late')), 300);
const electron = {
    webContents: {
        fromDevToolsTargetId: (targetId) => {
            if (targetId === 'view') return viewContents;
            return windows.find((window) => `window-${window.id}` === targetId)?.webContents;
        },
    },
    BrowserWindow: {
        getAllWindows: () => windows,
        fromId: (id) => windows.find((window) => window.id === id) ?? null,
        // The view is shown in the first window, but is not its own contents.
        fromWebContents: (contents) =>
            windows.find((window) => window.webContents === contents || (contents === viewContents && window.id === 1)),
    },
    screen: { getDisplayMatching: () => ({ scaleFactor: scenario === 'size-fractional' ? 1.5 : 1 }) },
};
// The titles that page.title() reads from the windows' own pages.
const pageTitles = { 1: 'First', 2: 'Second', 3: 'Late' };
if (scenario === 'page-title-none' || scenario === 'page-title-late') pageTitles[1] = '';
if (scenario === 'page-title-late') setTimeout(() => (pageTitles[1] = 'First'), 300);
// The own page of a window as Playwright sees it; its target id leads to the window's web contents.
const pageOf = (window) => ({ ...fakePage(`window-${window.id}`, context), title: async () => pageTitles[window.id] });
const viewPage = { ...fakePage('view', context), title: async () => 'View' };
// In one scenario, Playwright does not know the second window's page yet.
const known = (window) => !(scenario === 'page-title-no-page' && window.id === 2);
const page = pageOf(windows.find((window) => window.id === 1));
const app = {
    firstWindow: async () => page,
    windows: () => [viewPage, ...windows.filter(known).map(pageOf)],
    context: () => context,
    // The handle of the window that shows the active page, the first one.
    browserWindow: async () => ({
        evaluate: async (pageFunction) => pageFunction(windows.find((window) => window.id === 1)),
        dispose: async () => calls.push('dispose'),
    }),
    evaluate: async (pageFunction, arg) => pageFunction(electron, arg),
};
const playwright = { _electron: { launch: async () => app } };
const adoptContext = async () => ({ browserId: 'browser=app', contextId: 'context', pageId: 'page' });
const find = (window, timeout = 1000) =>
    electronJs.robotframeworkElectronWindowPage('browser=app', window, page, timeout);
// Adjusts a window, then forgets the calls before it and reports the window's state and size.
const adjust = async (window, state, size, timeout = 1000) => {
    await electronJs.robotframeworkElectronAdjustWindow('browser=app', window, state, size, page, timeout);
    return electronJs.robotframeworkElectronGetWindow('browser=app', window, page, 1000);
};
const prepare = (id, ...steps) => {
    const window = windows.find((window) => window.id === id);
    for (const step of steps) window[step]();
    calls.length = 0;
};
const fullScreen = (id) => {
    windows.find((window) => window.id === id).fullScreen = true;
};
const size = { width: 1024, height: 700 };
const scenarios = {
    'page-title-none': () => find('window=1', 300),
    'page-title-no-page': () => find('window=2', 300),
    'page-title-late': () => find('window=1', 2000),
    'get': () => electronJs.robotframeworkElectronGetWindow('browser=app', 'title=Second', page, 1000),
    'fullscreen-get': () => {
        fullScreen(1);
        return electronJs.robotframeworkElectronGetWindow('browser=app', null, page, 1000);
    },
    'maximize': () => adjust(null, 'maximized', null),
    'maximize-ignored': () => adjust(null, 'maximized', null, 300),
    'restore': () => {
        prepare(2, 'maximize', 'minimize');
        return adjust('window=2', 'normal', null);
    },
    'restore-transient': () => {
        prepare(2, 'maximize', 'minimize');
        return adjust('window=2', 'normal', null);
    },
    'fullscreen-restore': () => {
        fullScreen(1);
        return adjust(null, 'normal', null);
    },
    'fullscreen-maximize': () => {
        fullScreen(1);
        return adjust(null, 'maximized', null);
    },
    'size-maximized': () => {
        prepare(1, 'maximize');
        return adjust(null, 'normal', size);
    },
    'size-fractional': () => adjust(null, 'normal', size),
    'size-off': () => adjust(null, 'normal', size, 300),
    'size-reset': () => adjust(null, 'normal', size),
    'windows-all': () => electronJs.robotframeworkElectronWindows('browser=app', false, page, 1000),
    'windows-active': () => electronJs.robotframeworkElectronWindows('browser=app', true, page, 1000),
    'find-id': () => find('window=2'),
    'find-number': () => find('2'),
    'find-title': () => find('title=Second'),
    'find-active': () => find(null),
    'find-late': () => find('title=Late', 3000),
    'find-unknown': () => find('window=9'),
    'find-page': () => find('page=abc'),
    'find-twice': () => find('title=Second', 300),
    'find-missing': () => find('title=Missing', 300),
    'find-expression': () => find('title=/^sec/i'),
    'find-expression-twice': () => find('title=/s/i', 300),
    'find-expression-invalid': () => find('title=/(/'),
    // Not an expression: "user" holds letters that are no flags.
    'find-slashes': () => find('title=/home/user', 300),
};
(async () => {
    const launchArguments = ['/electron', [], {}, '/cwd', 1000, null, null, null, '/traces', {}];
    await electronJs.robotframeworkElectronLaunch(...launchArguments, playwright, adoptContext);
    return scenarios[scenario]();
})()
    .then((result) => ({ result }), (error) => ({ error: error.message }))
    .then((outcome) => console.log(JSON.stringify({ ...outcome, calls })));
"""


def run(tmp_path: Path, scenario: str, harness_code: str = HARNESS) -> dict[str, Any]:
    harness = tmp_path / "harness.js"
    harness.write_text(FAKE_PAGES + harness_code)
    completed = subprocess.run(
        ["node", str(harness), str(ELECTRON_JS), scenario], capture_output=True, text=True, check=True, timeout=30
    )
    outcome: dict[str, Any] = json.loads(completed.stdout)
    return outcome


def test_returns_the_adopted_context(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["result"] == {"browserId": "browser", "contextId": "context", "pageId": "page", "videoPath": None}
    assert outcome["calls"] == ["launch", "firstWindow", "adoptContext"]


def test_application_decides_the_color_scheme_by_default(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["options"]["launch"]["colorScheme"] is None
    assert outcome["options"]["adopt"] == {"acceptDownloads": True, "colorScheme": None}


def test_launch_options_reach_playwright_and_browser(tmp_path):
    outcome = run(tmp_path, "options")

    expected = {"acceptDownloads": True, "colorScheme": "dark", "locale": "de-DE", "bypassCSP": True}
    assert {key: outcome["options"]["launch"][key] for key in expected} == expected
    assert outcome["options"]["adopt"] == expected


def test_temporary_trace_files_go_to_the_given_folder(tmp_path):
    outcome = run(tmp_path, "success")

    assert outcome["options"]["launch"]["tracesDir"] == "/traces"


def test_starts_nothing_without_the_hook(tmp_path):
    outcome = run(tmp_path, "no-hook")

    assert "no adoptContext hook" in outcome["error"]
    assert outcome["calls"] == []


@pytest.mark.parametrize(
    ("scenario", "error", "calls"),
    [
        ("no-window", "no window", ["launch", "firstWindow", "close"]),
        ("adopt-fails", "adopt failed", ["launch", "firstWindow", "adoptContext", "close"]),
        ("close-fails", "adopt failed", ["launch", "firstWindow", "adoptContext", "close", "kill"]),
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

    assert outcome["error"] == f"Browser '{browser_id}' is not an application started by 'Start Electron Application'."


@pytest.mark.parametrize(("scenario", "active_page"), [("view-first", "window"), ("first-closed", None)])
def test_makes_the_window_page_the_active_page(tmp_path, scenario, active_page):
    outcome = run(tmp_path, scenario)

    assert outcome["options"]["activePage"] == active_page


def test_lists_the_windows_in_the_order_they_opened(tmp_path):
    outcome = run(tmp_path, "windows-all", WINDOWS_HARNESS)

    assert outcome["result"] == [{"id": 1, "title": "First"}, {"id": 2, "title": "Second"}]


def test_lists_the_window_of_the_active_page(tmp_path):
    outcome = run(tmp_path, "windows-active", WINDOWS_HARNESS)

    assert outcome["result"] == [{"id": 1, "title": "First"}]


@pytest.mark.parametrize("scenario", ["find-id", "find-number", "find-title"])
def test_finds_a_window_by_id_or_title_with_the_title_of_its_page(tmp_path, scenario):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["result"] == {"id": 2, "pageTitle": "Second"}


def test_finds_the_window_of_the_active_page(tmp_path):
    outcome = run(tmp_path, "find-active", WINDOWS_HARNESS)

    assert outcome["result"] == {"id": 1, "pageTitle": "First"}
    assert outcome["calls"] == ["dispose"]


def test_waits_for_a_window_with_the_title(tmp_path):
    outcome = run(tmp_path, "find-late", WINDOWS_HARNESS)

    assert outcome["result"] == {"id": 3, "pageTitle": "Late"}


def test_finds_a_window_by_a_regular_expression_with_flags(tmp_path):
    outcome = run(tmp_path, "find-expression", WINDOWS_HARNESS)

    assert outcome["result"] == {"id": 2, "pageTitle": "Second"}


@pytest.mark.parametrize(
    ("scenario", "error"),
    [
        ("find-expression-twice", "2 windows show a title that matches /s/i: window=1, window=2."),
        ("find-expression-invalid", "'title=/(/' is no valid regular expression: "),
        ("find-slashes", "No window shows the title '/home/user'."),
    ],
)
def test_finding_by_a_regular_expression_fails_without_exactly_one_window(tmp_path, scenario, error):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["error"].startswith(error)


def test_waits_until_the_page_of_a_window_has_a_title(tmp_path):
    outcome = run(tmp_path, "page-title-late", WINDOWS_HARNESS)

    assert outcome["result"] == {"id": 1, "pageTitle": "First"}


@pytest.mark.parametrize(("scenario", "window"), [("page-title-none", 1), ("page-title-no-page", 2)])
def test_reports_no_title_for_a_window_without_a_page_with_a_title(tmp_path, scenario, window):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["result"] == {"id": window, "pageTitle": None}


@pytest.mark.parametrize(
    ("scenario", "error"),
    [
        ("find-unknown", "The application has no window 'window=9'."),
        (
            "find-page",
            "'page=abc' names no window. Give a window as 'title=<title>' or as an id from 'Get Window Ids'.",
        ),
        ("find-twice", "2 windows show the title 'Second': window=2, window=3."),
        ("find-missing", "No window shows the title 'Missing'."),
    ],
)
def test_finding_fails_without_exactly_one_window(tmp_path, scenario, error):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["error"] == error


def without_handles(calls: list[str]) -> list[str]:
    """The calls without the disposals of the handles of the active page's window."""
    return [call for call in calls if call != "dispose"]


def test_reports_the_state_and_content_size(tmp_path):
    outcome = run(tmp_path, "get", WINDOWS_HARNESS)

    assert outcome["result"] == {"state": "normal", "width": 800, "height": 600}


def test_maximises_a_window(tmp_path):
    outcome = run(tmp_path, "maximize", WINDOWS_HARNESS)

    assert outcome["result"]["state"] == "maximized"
    assert without_handles(outcome["calls"]) == ["maximize 1"]


def test_names_the_likely_causes_when_the_window_manager_ignores_a_change(tmp_path):
    outcome = run(tmp_path, "maximize-ignored", WINDOWS_HARNESS)

    assert outcome["error"].startswith("The window 'window=1' is normal, not maximized, after 300 ms.")
    assert "a display without a window manager" in outcome["error"]


@pytest.mark.parametrize("scenario", ["restore", "restore-transient"])
def test_restores_a_window_that_was_maximised_before_it_was_minimised(tmp_path, scenario):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["result"]["state"] == "normal"
    assert outcome["calls"] == ["restore 2", "unmaximize 2"]


def test_reports_a_fullscreen_window_as_maximised(tmp_path):
    outcome = run(tmp_path, "fullscreen-get", WINDOWS_HARNESS)

    assert outcome["result"]["state"] == "maximized"


@pytest.mark.parametrize(
    ("scenario", "state", "calls"),
    [
        ("fullscreen-restore", "normal", ["setFullScreen 1 false"]),
        ("fullscreen-maximize", "maximized", ["setFullScreen 1 false", "maximize 1"]),
    ],
)
def test_leaves_fullscreen_before_a_change(tmp_path, scenario, state, calls):
    outcome = run(tmp_path, scenario, WINDOWS_HARNESS)

    assert outcome["result"]["state"] == state
    assert without_handles(outcome["calls"]) == calls


def test_sizes_a_maximised_window_after_restoring_it(tmp_path):
    outcome = run(tmp_path, "size-maximized", WINDOWS_HARNESS)

    assert outcome["result"] == {"state": "normal", "width": 1024, "height": 700}
    assert without_handles(outcome["calls"]) == ["unmaximize 1", "setContentSize 1"]


def test_asks_again_for_a_size_that_the_window_manager_reset(tmp_path):
    outcome = run(tmp_path, "size-reset", WINDOWS_HARNESS)

    assert outcome["result"] == {"state": "normal", "width": 1024, "height": 700}
    assert without_handles(outcome["calls"]) == ["setContentSize 1", "setContentSize 1"]


def test_allows_a_pixel_off_at_a_fractional_display_scale(tmp_path):
    outcome = run(tmp_path, "size-fractional", WINDOWS_HARNESS)

    assert outcome["result"] == {"state": "normal", "width": 1023, "height": 701}


def test_names_the_size_that_the_window_got(tmp_path):
    outcome = run(tmp_path, "size-off", WINDOWS_HARNESS)

    assert outcome["error"].startswith(
        "The window 'window=1' has the content size 1023x701, not 1024x700, after 300 ms."
    )
