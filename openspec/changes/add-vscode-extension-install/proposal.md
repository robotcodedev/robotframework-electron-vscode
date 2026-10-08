# Proposal

## Why

`Open VS Code` installs extensions only before VS Code starts. Some tests need an extension installed while VS Code is running, for example to check how the extension under test reacts when another extension arrives. A test cannot do that itself: it would need the instance's command-line script and its user-data and extensions directories. It would also have to remove the `VSCODE_*` variables that connect the script to the user's own VS Code. The feature spike on 2026-10-08 showed that VS Code 1.141 picks up an extension installed with the command-line script into a running instance right away, without a reload.

## What Changes

- New keyword `Install VS Code Extension` in the `VSCode` library. It installs a Marketplace extension or a `.vsix` file into a running instance that `Open VS Code` started, by default the active one. It uses the same command-line script, directories and environment as the `extensions` argument of `Open VS Code`, so forks install from their own gallery.
- `Open VS Code` remembers, for each instance it starts, the executable and the instance directories, so that the keyword can find them.
- The library's boundary grows by this keyword: besides `Open VS Code` and `Close VS Code`, `VSCode` adds `Install VS Code Extension` to the keywords of `Electron`. It drives VS Code's command line, not the workbench, so the rule that workbench keywords belong to projects still holds.
- The getting-started page for VS Code extensions mentions the keyword.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-launch`: adds installing extensions into a running instance.
- `vscode-examples`: the library's keywords beyond those of `Electron` now include `Install VS Code Extension`.

## Impact

- `packages/vscode/src/VSCode/__init__.py`: the keyword and a small per-instance record.
- `packages/vscode/tests/` and `packages/vscode/atest/`: tests, and a helper that packs the test extension into a `.vsix`.
- `docs/src/content/docs/getting-started/vscode.md`.
