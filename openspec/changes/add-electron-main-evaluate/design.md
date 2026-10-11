# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements.
- **Starting:** `electron.js` starts an application with `playwright._electron.launch` and hands its context to Browser with the `adoptContext` hook. Browser keeps the context, but nothing keeps the `ElectronApplication` object.
- **The hook:** `adoptContext(context, { onClose })` calls `onClose` once when Browser closes the browser.
- **Evaluating:** `electronApplication.evaluate(pageFunction, arg)` serialises the function, runs it in the main process with the `electron` module as first argument, and returns its JSON-serialisable result. Handles in `arg` arrive as the objects they point to.
- **Windows:** `electronApplication.browserWindow(page)` returns a handle on the `BrowserWindow` of a page. Playwright finds it in the main process with `webContents.fromDevToolsTargetId` and `BrowserWindow.fromWebContents`, which returns `null` if no window owns the page's contents.
- **Browser's injection:** Browser passes JavaScript extension functions the active page as the parameter `page`, but no other page.

## Goals / Non-Goals

**Goals:**
- One keyword with the semantics of Playwright's `electronApplication.evaluate`, for any application started by `New Electron Application`, including VS Code.

**Non-Goals:**
- Keywords for single main-process tasks, such as replacing dialogs or sizing windows. The guides show them as short functions for this keyword.
- Waiting for main-process events (`electronApplication.waitForEvent`), and access to the extension host of VS Code, which is a separate Node process.

## Decisions

### Keyword

```
Evaluate In Main Process    function    arg=None    browser=CURRENT
```

- `function` is the text of a JavaScript function, as for Browser's `Evaluate JavaScript`. Its parameters are the `electron` module, `arg` and `window`.
- `arg` is any JSON-serialisable value.
- `window` is the `BrowserWindow` that shows the active page, if the active page belongs to the application. Otherwise it is `null`: another browser is active, or no window owns the page.
- `browser` is `CURRENT` or a browser id that `New Electron Application` returned. `CURRENT` is resolved with `Get Browser Ids    ACTIVE`, as for `Get VS Code Instance Directories`.
- The keyword returns the function's result, and logs it like `Evaluate JavaScript`.
- **Alternative:** an argument `page` with a page id. Rejected: Browser gives extension functions only the active page, and tests choose pages with `Switch Page` anyway, as for `Evaluate JavaScript`.
- **Alternative:** keywords for windows, such as setting their bounds. Rejected for the reason in the non-goals: the guides show them as short functions.

### Applications in `electron.js`

- A module-level `Map` holds each started `ElectronApplication` under its browser id.
- `robotframeworkElectronLaunch` adds the application after `adoptContext` and passes an `onClose` option that removes it again.
- A new function `robotframeworkElectronEvaluate(browserId, script, arg, page)` looks the application up and fails with a message that names the browser id if there is none.
- It gets `window` with `application.browserWindow(page)` if `page.context()` is the application's context, and uses `null` otherwise.
- It calls `application.evaluate` with a fixed wrapper function and `{ script, arg, window }` as argument. In the main process, the wrapper turns `script` into a function with `new Function('return (' + script + ')')()` and calls it with the `electron` module, `arg` and `window`.
  - Playwright serialises only the wrapper's text. The test's function therefore travels as data, and `window` as a handle in the argument.
  - A string passed to Playwright directly would be evaluated as an expression, so a function text would be returned instead of run.

### Fixture

- **Preload and IPC:** the fixture app gets a preload script that exposes `window.fixture.openFile()` through `contextBridge`. In `main.js`, `ipcMain.handle('open-file')` calls `dialog.showOpenDialog` and returns the first path or an empty string.
- **Button:** `index.html` gets a button `id=open-file` and an element `id=opened`, which shows the returned path.
- **Native dialog:** the tests click the button only after they have replaced `dialog.showOpenDialog`, so a native dialog never opens.

### Documentation

- **Getting started for Electron:** a section *The main process* with the dialog example.
- **Browser features guide:** the row for native dialogs points to the keyword.
- **Video guide:** sizing the window with `window.setBounds` as the alternative to a window manager. That is how Microsoft's smoke tests size VS Code for their videos.

## Risks / Trade-offs

- [`<webview>` guests and `WebContentsView`s as active page] → `BrowserWindow.fromWebContents` may return the window that hosts them, or `null`. The acceptance tests check this with the fixture app, and the keyword documentation says what `window` is for them.
- [Applications that disable the Node inspector] → They cannot be started by Playwright in the first place, so nothing changes.
- [A function that returns non-serialisable values, such as a `BrowserWindow`] → Playwright fails with its own message; the keyword documentation says to return plain values.
