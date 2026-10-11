# Proposal

## Why

VS Code's command-line script can do much more with extensions than the libraries offer:
- install a fixed version (`publisher.name@1.2.3`) or a pre-release (`--pre-release`);
- uninstall, list and update extensions;
- work with profiles.

`Install VS Code Extension` covers one of these uses, installing into a running instance. It is flaky on CI: VS Code's shared process may not notice an extension that the script installs right after the start (the test "Extension In A Running Instance" failed in both CI runs on 2026-10-11).

Users who want any of the other uses today have to find the script themselves and call it with Robot Framework's Process library. That has two traps:

- **Missing directories:** without `--extensions-dir` and `--user-data-dir`, the script works on the user's own VS Code.
- **Inherited environment:** in a test run started from VS Code's terminal, the inherited `VSCODE_IPC_HOOK_CLI` sends the call to the user's running VS Code instead of the test instance.

Preparing extensions once and reusing them in every test, which is faster and works offline, is not possible at all, because `Open VS Code` always starts with an empty extensions directory.

Rather than a keyword for every use case, the libraries offer the building blocks, and the documentation shows how to combine them.

## What Changes

- **Run VS Code's command line:** a new keyword `Execute VS Code CLI Command` in `VSCode.Helper`.
  - It runs the command-line script of a VS Code build, selected like `Open VS Code` does (`version`, `executable`, `cache_dir`), with any arguments.
  - The extensions directory and the user-data directory are required arguments, so a call cannot reach the user's own VS Code by accident.
  - It removes the variables that tie a process to a running VS Code from the environment.
  - It returns the script's output and fails with that output if the script reports an error.
- **The directories of an instance:** a new keyword `Get VS Code Instance Directories` in `VSCode`. It returns the root, user-data and extensions directories of an instance that `Open VS Code` started, for use with `Execute VS Code CLI Command` or to read its logs.
- **A prepared extensions directory:** `Open VS Code` gets the argument `extensions_dir`. With it, the instance uses that directory instead of an empty one of its own. Keeping instances apart is then up to the test, for example by copying a prepared directory for each test.
- **Recipes in the documentation:** the guide on extensions shows every way to get extensions into a test instance:
  - from source;
  - at the start;
  - into a running instance;
  - prepared once and copied for each test;
  - fixed versions and pre-releases;
  - uninstalling and listing;
  - disabling extensions with `args`;
  - workspace recommendations;
  - profiles.
- **Example:** the example project prepares the Python extension once with `Execute VS Code CLI Command` and opens VS Code with a copy of it.
- **`extensions` of `Open VS Code` is removed.** Installing extensions is left to the tests: `Execute VS Code CLI Command` installs them into a directory, and `Open VS Code` starts with a copy of it through `extensions_dir`. The example and the guide show this as the way to start VS Code with extensions.
- **`Install VS Code Extension` is removed.** It only ran the command-line script with the instance's directories, which `Execute VS Code CLI Command` and `Get VS Code Instance Directories` now do. The recipe "into a running instance" explains the part the keyword never handled: waiting until the running instance reports the extension in its shared process log, and installing it again if the report does not come. The example's test "Installed While Running" uses this recipe.

## Capabilities

### New Capabilities

- `vscode-command-line`: running VS Code's command-line script against explicitly given directories, from `VSCode.Helper`.

### Modified Capabilities

- `vscode-launch`: `Open VS Code` can use a given extensions directory, and `Get VS Code Instance Directories` returns the directories of an instance. The requirements "Dependency extensions" and "Install extensions into a running instance" are removed. "Open VS Code" and "VS Code forks" no longer install extensions themselves.
- `vscode-examples`: the example prepares the Python extension once and copies it before the start, installs into a running instance with the recipe, and the library's added keywords change. The guide on dependency extensions becomes the guide on extensions.

## Impact

- `packages/vscode/src/VSCode/Helper.py`: `Execute VS Code CLI Command`.
- `packages/vscode/src/VSCode/__init__.py`: the `extensions_dir` argument, `Get VS Code Instance Directories`, and the removal of `extensions` and `Install VS Code Extension`.
- `packages/vscode/src/VSCode/instance.py`: the instance directories with a given extensions directory, and the removal of `install_extensions`.
- Unit tests in `packages/vscode/tests/`, acceptance tests in `packages/vscode/atest/`, where `install_extension.robot` is replaced.
- `docs/src/content/docs/guides/extensions.mdx`, `vscode-forks.md`, `workbench-keywords.mdx`, `docs/src/content/docs/getting-started/vscode.md` and the example project in `examples/vscode-extension/`, including its video tests.
- No change to the Browser library.
