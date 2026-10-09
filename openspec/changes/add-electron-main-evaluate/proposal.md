# Proposal

## Why

Browser keywords reach an Electron application's windows, but not its main process. Some things are only possible there:
- **Native dialogs:** file dialogs and message boxes are outside the page. A test can only replace them, in the main process, before the application opens them.
- **Window size:** without a window manager, the window can still be sized with `BrowserWindow.setBounds`. Microsoft's smoke tests for VS Code size the window this way for their 1920×1080 videos.
- **Application state:** for example `app.getPath`, `app.getVersion`, or a check of what the main process received through IPC.

Playwright offers this as `electronApplication.evaluate(pageFunction, arg)`, which runs a function in the main process with the `electron` module as its first argument. `New Electron Application` keeps no handle on the application, so there is no keyword for it.

## What Changes

- **New keyword:** `Evaluate In Main Process    function    arg=None    browser=CURRENT` in the `Electron` library. It runs a JavaScript function in the main process of an application started by `New Electron Application`, by default the active one. The function gets the `electron` module and `arg`, and the keyword returns the function's result.
- **VS Code:** inherits the keyword, so it works for instances started by `Open VS Code` as well.
- **Fixture:** the Electron fixture app gets a button that opens a native file dialog through IPC and shows the chosen path, so that the tests can replace the dialog.
- **Documentation:** the getting-started page for Electron shows how to replace a native dialog, and the guides name the keyword for native dialogs and for sizing windows without a window manager.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: running code in the application's main process.
- `vscode-launch`: the keyword works for VS Code instances.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`.
- The Electron fixture app (`main.js`, a preload script, `index.html`) and acceptance tests in both packages.
- `docs/`: the getting-started page for Electron, the Browser features guide and the video guide.
