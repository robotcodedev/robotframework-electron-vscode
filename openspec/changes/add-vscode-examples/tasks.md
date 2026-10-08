# Tasks

## 1. Example project

- [x] 1.1 Create the example extension in `examples/vscode-extension/` (`package.json`, `extension.js` with `Say Hello`, `Pick` and `Open Webview`) and its `robot.toml` (paths, output directory). Verify that `uv run robotcode -r examples/vscode-extension discover tests` runs and that the extension's commands work in an instance opened by `Open VS Code`.
- [x] 1.2 Write `tests/resources/vscode.resource` (`${VSCODE_VERSION}`, `${VSCODE_EXECUTABLE}`, `${VSCODE_CACHE}`, `Open Example VS Code`) and one resource per workbench part, each with its keywords and its locators as variables: `command_palette.resource` (`Run Command`), `quick_pick.resource` (`Select Quick Pick Item`), `notifications.resource` (`Notification Should Be Shown`) and `webview.resource` (`Enter Webview`, `Leave Webview`). Each resource imports what it uses. Check the webview frame selectors against VS Code 1.141. Verify with `uv run robotcode -r examples/vscode-extension analyze code` that no errors or warnings are reported.
- [x] 1.3 Write `commands.robot`, `quick_pick.robot` and `webview.robot` for the spec scenarios "Command through the command palette", "Quick pick" and "Webview". Verify that `uv run robotcode -r examples/vscode-extension robot` passes.
- [x] 1.4 Add a profile to the example's `robot.toml` that overrides one locator with an equivalent selector, and a comment on profiles per VS Code version. Verify the scenario "Locator overridden by a profile" by running the example with that profile and checking in `robotcode results log` that the overridden locator was used.
- [x] 1.5 Verify the scenario "Copied example": copy the folder to a temporary directory and run it there from its own root.
- [x] 1.6 Write the example's `README.md`: what it shows, how to run it, and links to the two guides. Verify that the commands in it run as written.

## 2. Library and documentation

- [x] 2.1 Remove `VSCodeInstance` and the instance registry from `VSCode`, and add a pytest test that the only keywords `VSCode` adds to those of `Electron` are `Open VS Code` and `Close VS Code`. Verify that `uv run pytest` and the library's acceptance tests pass.
- [x] 2.2 Write the guides `docs/src/content/docs/guides/workbench-keywords.mdx` and `vscode-versions.mdx`. They include the example's files with `?raw` and `<Code>` and explain the important points from the design. Verify the scenarios "Guide on workbench keywords" and "Guide on VS Code versions" with `npm run build` in `docs/`. Then verify the documentation-site scenario "Changed example file": change an example file, rebuild, check that the guide shows the change, and revert it.
- [x] 2.3 Add the example run to the commands in `AGENTS.md`. Verify that the command runs as written.
