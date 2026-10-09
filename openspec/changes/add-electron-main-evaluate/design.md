# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements.
- **Starting:** `electron.js` starts an application with `playwright._electron.launch` and hands its context to Browser with the `adoptContext` hook. Browser keeps the context, but nothing keeps the `ElectronApplication` object.
- **The hook:** `adoptContext(context, onClose)` calls `onClose` once when Browser closes the browser.
- **Evaluating:** `electronApplication.evaluate(pageFunction, arg)` serialises the function, runs it in the main process with the `electron` module as first argument, and returns its JSON-serialisable result.

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

- `function` is the text of a JavaScript function, as for Browser's `Evaluate JavaScript`. Its first parameter is the `electron` module, and its second is `arg`.
- `arg` is any JSON-serialisable value.
- `browser` is `CURRENT` or a browser id that `New Electron Application` returned. `CURRENT` is resolved with `Get Browser Ids    ACTIVE`, as for `Install VS Code Extension`.
- The keyword returns the function's result, and logs it like `Evaluate JavaScript`.

### Applications in `electron.js`

- A module-level `Map` holds each started `ElectronApplication` under its browser id.
- `robotframeworkElectronLaunch` adds the application after `adoptContext` and passes an `onClose` that removes it again.
- A new function `robotframeworkElectronEvaluate(browserId, script, arg)` looks the application up and fails with a message that names the browser id if there is none. It turns `script` into a function with `new Function('return (' + script + ')')()` and calls `application.evaluate(fn, arg)`. A string passed to Playwright directly would be evaluated as an expression, so a function text would be returned instead of run.

### Fixture

- **Preload and IPC:** the fixture app gets a preload script that exposes `window.fixture.openFile()` through `contextBridge`. In `main.js`, `ipcMain.handle('open-file')` calls `dialog.showOpenDialog` and returns the first path or an empty string.
- **Button:** `index.html` gets a button `id=open-file` and an element `id=opened`, which shows the returned path.
- **Native dialog:** the tests click the button only after they have replaced `dialog.showOpenDialog`, so a native dialog never opens.

### Documentation

- **Getting started for Electron:** a section *The main process* with the dialog example.
- **Browser features guide:** the row for native dialogs points to the keyword.
- **Video guide:** sizing the window with `setBounds` as the alternative to a window manager. That is how Microsoft's smoke tests size VS Code for their videos.

## Risks / Trade-offs

- [`new Function` runs code from the test in the Node process of Browser] → It only builds the function from the text that the test passes, as `Evaluate JavaScript` does for pages. It runs in the application's main process, not in the Node process.
- [Applications that disable the Node inspector] → They cannot be started by Playwright in the first place, so nothing changes.
- [A function that returns non-serialisable values, such as a `BrowserWindow`] → Playwright fails with its own message; the keyword documentation says to return plain values.
