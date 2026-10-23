# Proposal

## Why

A test of a desktop application works with windows, but the libraries offer only Browser's page keywords for them. A window can be sized, maximised, minimised or restored only through `Evaluate In Main Process` and Electron's `BrowserWindow` API, or for VS Code through its setting `window.newWindowDimensions`. So in a test run nothing maximises or resizes a window unless the test writes main-process code. Switching to a window that the application opens works with `Switch Page    NEW`, but that can land on a `WebContentsView` or `<webview>` that loads after the window, and `Get Page Ids` mixes windows with these views.

## What Changes

- **Window ids:** a window's id is Electron's id of its `BrowserWindow` with the prefix `window=`, for example `window=2`, read in the main process. It is valid while the application runs, as Browser's page ids are, and unique within the application. `Get Window Ids` returns the ids of the active application's windows, which leaves views and `<webview>`s out, and with `ACTIVE` the id of the window that shows the active page.
- **Window titles:** `Get Window Titles` returns the titles that the windows show, which is how a user tells windows apart on the desktop.
- **Giving a window:** the window keywords take a window by its title, for example `title=Settings`, or by its id. For a title, they wait until a window shows it, so that a test can name a window that is still opening.
- **Switching:** `Switch Window` makes a window's own page the active page, given by title, by window id, by page id as `Switch Page` takes it, or with `NEW`, and returns the id of the page that was active before. It finds the window's page in Browser's catalog by the page's title, which the catalog and the main process both know, and checks after switching that the active page is that window's own page.
- **Size:** `Set Window Size` and `Get Window Size` set and return a window's content size: the area that its page, its screenshots and its video show.
- **State:** `Maximize Window`, `Minimize Window` and `Restore Window` change a window's state, and `Get Window State` returns `normal`, `maximized` or `minimized`.
- **Which window:** without a window, the size and state keywords act on the window that shows the active page; with one, on that window, and the active page stays as it is.
- **Getters with assertions:** `Get Window Size` and `Get Window State` take Browser's assertion operators, as `Get Viewport Size` does.
- **Waiting:** the keywords return once the window has the new size or state. If the window manager does not apply a change within the library timeout, they fail with an error that names the likely cause, for example a display without a window manager, or a desktop that cannot minimise windows.
- **No Browser change:** nothing relies on Browser's internals. `Switch Window` uses `Switch Page`, with the page id that Browser's catalog lists for the title of the window's page.
- **Unchanged:** Browser's page keywords stay as they are. Page ids remain the ids for what a test clicks and reads, and the way to select views and `<webview>`s. There is no `Close Window`, because `Close Page` already closes windows. The VSCode library gets the keywords too, because it provides every keyword of Electron.
- **Documentation:** the guides describe the window keywords instead of the main-process workaround for sizing and maximising, explain window titles, window ids and page ids, recommend the title for switching to a new window, and say that a minimised window draws nothing until it is restored.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: new requirements for finding and switching windows, for their size, and for their state.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, with unit tests in `packages/electron/tests/`.
- Tests of the window keywords in the existing suite `packages/electron/atest/windows.robot`, with a second window of the fixture app that shows a `<webview>`, and a check in `packages/vscode/atest/` that the keywords work on VS Code.
- Documentation: the Electron guides on Browser keywords and on getting started, the guide on CI and the Linux display, the VS Code guides on Browser keywords, on videos and traces and on the extension host, the Electron library's introduction on windows and pages, and the keyword documentation of `Start Electron Application`, `Evaluate In Main Process` and VSCode's `Evaluate In Extension Host`.
- The example's `windows.robot`, to which the VS Code guide on Browser keywords points, switches windows with `Switch Window`.
- No change to the Browser library.
- Existing keywords keep their behaviour.
