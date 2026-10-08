# Proposal

## Why

The earlier plan `add-vscode-workbench` put workbench keywords and a version-dependent locator table into the VSCode library. The workbench DOM, however, changes with VS Code releases, differs between versions and forks, and every extension needs other parts of it. If the library owned these locators, users would have to wait for a release of the library whenever VS Code changes.

The libraries therefore provide only the technique: downloading VS Code, starting it in isolation, and handing its windows to Browser. Keywords and locators for the workbench belong to the user's project. The repository shows with runnable examples how to write them.

## What Changes

- The planned change `add-vscode-workbench` is dropped. There will be no workbench keywords, no locator table and no `Set VS Code Selector` in the library.
- New example project `examples/vscode-extension/`: a small, self-contained extension with its own `robot.toml` and tests. It can be copied as a starting point. Its own resources define keywords and locators for:
  - running a command through the command palette, waiting for the command's row first,
  - selecting a quick pick item,
  - reading notifications,
  - acting inside an extension's webview.
- In the example, the locators are variables, and a project overrides them per VS Code version with profiles in `robot.toml`.
- The examples run with the repository's tests, so they stay working with the current libraries and VS Code.
- Two guides on the documentation site explain the example: writing your own workbench keywords and locators, and profiles per VS Code version. They include the example's files instead of copying them. The example therefore keeps each workbench part in a resource file of its own, so that a guide section can show a whole file.
- The `VSCode` library drops its unused instance registry, which was kept for the locator table.

## Capabilities

### New Capabilities

- `vscode-examples`: the boundary between the library and the user's project, and the runnable examples that show how a project drives the VS Code workbench with its own keywords and locators.

### Modified Capabilities

None.

## Impact

- A new folder `examples/vscode-extension/`, which is not part of any package.
- `packages/vscode/`: a small cleanup in `__init__.py`.
- `docs/`: the two guides. This change builds on `add-documentation-site`, which is applied first.
- `AGENTS.md`: the command that runs the examples.
- The example tests download VS Code into the user's cache directory on first use, like any user project.
