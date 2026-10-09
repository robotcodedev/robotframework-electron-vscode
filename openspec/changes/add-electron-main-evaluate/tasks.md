# Tasks

## 1. Electron

- [ ] 1.1 Keep the started applications in `electron.js`, add `robotframeworkElectronEvaluate` and the keyword `Evaluate In Main Process` with documentation, and a pytest test for the keyword's arguments. Verify that `uv run pytest` passes.
- [ ] 1.2 Add the preload script, the IPC handler and the button to the fixture app, and acceptance tests for "Value from the main process", "Native dialog replaced", "Window sized from the main process" and "Not an Electron application". Verify that the Electron acceptance tests pass.

## 2. VS Code

- [ ] 2.1 Add an acceptance test for "VS Code's version from its main process". Verify that the VSCode acceptance tests pass and that `analyze code` reports no errors or warnings.

## 3. Documentation

- [ ] 3.1 Add the section on the main process to the getting-started page for Electron, the dialog row to the Browser features guide and `setBounds` to the video guide. Verify their snippets in a RobotCode REPL session or a scratch suite, and that `npm run build` in `docs/` succeeds with no broken links.
