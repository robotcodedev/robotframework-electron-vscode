# Tasks

## 1. Electron

- [ ] 1.1 Keep the started applications in `electron.js`, add `robotframeworkElectronEvaluate` with the window of the active page, and the keyword `Evaluate In Main Process` with documentation. Add pytest tests for the keyword's arguments and, in `test_electron_js.py`, for `window` with the application's page and with a page of another context. Verify that `uv run pytest` passes.
- [ ] 1.2 Add the preload script, the IPC handler and the button to the fixture app, and an acceptance test per scenario of the `electron-applications` delta. Check what `window` is for a page that is not a window of its own, such as a `<webview>` guest, and document it in the keyword. Verify that the Electron acceptance tests pass with `-p xvfb`.

## 2. VS Code

- [ ] 2.1 Add an acceptance test for "VS Code's version from its main process". Verify that the VSCode acceptance tests pass and that `analyze code` reports no errors or warnings.

## 3. Documentation

- [ ] 3.1 Add the section on the main process to the getting-started page for Electron, the dialog row to the Browser features guide and `window.setBounds` to the video guide. Verify their snippets in a RobotCode REPL session or a scratch suite, and that `npm run build` in `docs/` succeeds with no broken links.
