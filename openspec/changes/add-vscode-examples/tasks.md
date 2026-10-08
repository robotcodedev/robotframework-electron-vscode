# Tasks

## 1. Example project

- [ ] 1.1 Create the example extension in `examples/vscode-extension/` (`package.json`, `extension.js` with `Say Hello`, `Pick` and `Open Webview`) and its `robot.toml` (paths, output directory). Verify that `uv run robotcode -r examples/vscode-extension discover tests` runs and that the extension's commands work in an instance opened by `Open VS Code`.
- [ ] 1.2 Write `tests/resources/variables.resource` (`${VSCODE_VERSION}`, `${VSCODE_EXECUTABLE}`, `${VSCODE_CACHE}`) and `tests/resources/workbench.resource` with the keywords `Run Command`, `Select Quick Pick Item`, `Notification Should Be Shown`, `Enter Webview` and `Leave Webview`, and with all locators as variables. Check the webview frame selectors against VS Code 1.141. Verify with `robotcode -r examples/vscode-extension analyze code` that no errors or warnings are reported.
- [ ] 1.3 Write `commands.robot`, `quick_pick.robot` and `webview.robot` for the spec scenarios "Command through the command palette", "Quick pick" and "Webview". Verify that `uv run robotcode -r examples/vscode-extension robot` passes.
- [ ] 1.4 Add a profile to the example's `robot.toml` that overrides one locator with an equivalent selector, and a comment on profiles per VS Code version. Verify the scenario "Locator overridden by a profile" by running the example with that profile and checking in `robotcode results log` that the overridden locator was used.
- [ ] 1.5 Verify the scenario "Copied example": copy the folder to a temporary directory and run it there from its own root.
- [ ] 1.6 Write the example's `README.md`: what it shows, how to run it, what to adapt in a real project. Verify that the commands in it run as written.

## 2. Library and documentation

- [ ] 2.1 Remove `VSCodeInstance` and the instance registry from `VSCode`, and add a pytest test that the only keywords `VSCode` adds to those of `Electron` are `Open VS Code` and `Close VS Code`. Verify that `uv run pytest` and the library's acceptance tests pass.
- [ ] 2.2 Add a section to the README of `robotframework-vscode` that points to the example and names the important points, and add the example run to the commands in `AGENTS.md`. Verify the links and that the commands run as written.
