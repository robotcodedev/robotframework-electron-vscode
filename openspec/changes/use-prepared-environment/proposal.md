# Proposal

## Why

The test environment belongs to the person who runs the tests, and it is set before the tests start: which VS Code or Electron, which extensions, which user data, which workspace. The libraries still mix part of it into the tests:
- They download VS Code and Electron releases, cache and verify them, and select versions. That is about 500 lines of library code and 600 lines of unit tests.
- Ready-made tools already do this job: `@vscode/test-electron` downloads VS Code, and the npm package `electron` brings Electron.
- `Execute VS Code CLI Command` lives in a separate helper library and needs both directories, and the version or executable, on every call. Even for the VS Code instance that runs right now, a test first reads them with `Get VS Code Instance Directories`.
- The keywords that start an application are called `Open VS Code` and `New Electron Application`. Both start an application, so "Start" fits better.

## What Changes

- **Renamed keywords:** `Open VS Code` becomes `Start VS Code`, and `New Electron Application` becomes `Start Electron Application`. There are no aliases for the old names.
- **No downloads:** the libraries no longer download anything.
  - `Get VS Code Executable`, `Get Electron Executable`, and the arguments `version` and `cache_dir` of `Open VS Code` go away, together with the download code.
  - The helper libraries `VSCode.Helper` and `Electron.Helper` go away; nothing else remains in them.
  - `Start VS Code` takes the VS Code executable as its required first argument: an installed VS Code, a portable copy, a fork, or a build that a tool such as `@vscode/test-electron` downloaded.
- **Given directories:** `Start VS Code` gets `user_data_dir` next to `extensions_dir`.
  - Given directories are used as they are.
  - Directories that are not given are created fresh in the instance's folder, as now.
  - The library writes its default settings and `settings` only into a user-data directory that it created. `settings` together with `user_data_dir` fails.
- **The command-line script with the instance:** `Execute VS Code CLI Command` moves into the `VSCode` library and takes the same environment arguments as `Start VS Code`:
  - Without `executable`, `user_data_dir` and `extensions_dir`, it uses the active VS Code instance: its executable, its directories and its environment.
  - With them, it uses the environment that `Start VS Code` would get with the same arguments, for example to prepare an extensions directory before the start.
- **This repository:** the acceptance tests, the CI and the example get VS Code from `@vscode/test-electron` and Electron from the npm package `electron`, through npm scripts. `robot.toml` variables and profiles point to the executables.
- **Documentation:**
  - the guide "Downloads and cache" goes away;
  - the guide on VS Code versions shows profiles that point to executables;
  - the getting-started pages, the guides on CI, forks, extensions and workbench keywords, and the READMEs follow the new keywords.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-launch`:
  - `Start VS Code` with a required executable, and `user_data_dir`;
  - settings only for user-data directories that the library created;
  - the renamed keywords in every requirement;
  - documentation without the helper library.
- `electron-applications`: `Start Electron Application` in every requirement, and keyword documentation without `Electron.Helper`.
- `vscode-command-line`: `Execute VS Code CLI Command` in the `VSCode` library, on the active instance or on the environment given as for `Start VS Code`.
- `vscode-examples`:
  - the library's keywords;
  - the example gets its VS Code with `@vscode/test-electron`, also when copied out of the repository.
- `vscode-extension-host`, which `add-vscode-extension-host-evaluate` adds: the renamed keywords.
- `vscode-download` and `electron-download`: all requirements are removed, and the change retires both capabilities.

## Impact

- **Library code:**
  - `packages/vscode/src/VSCode/__init__.py`: `Start VS Code` and `Execute VS Code CLI Command`;
  - `packages/vscode/src/VSCode/instance.py`: the directories of an instance and of a script call;
  - `packages/electron/src/Electron/__init__.py`: `Start Electron Application`;
  - removed: `VSCode/Helper.py`, `VSCode/download.py` and `Electron/Helper.py`. The parts of `download.py` that work on an installed VS Code, such as finding the command-line script, move to the library.
- **Tests:**
  - the unit tests of the downloads and of the helper libraries go away;
  - the unit tests of the libraries follow the new keywords;
  - every acceptance test that starts an application uses the new names and an executable from the variables.
- **Repository:**
  - a `package.json` in the root with `@vscode/test-electron` and `electron`, and an npm script that prepares the builds for the tests;
  - `robot.toml` and its profiles;
  - the CI's test job;
  - the example's `package.json` and `robot.toml`;
  - `docs/scripts/update_screenshots.py`.
- **Documentation:** the guides and pages named above, and the READMEs of both packages.
- **Order:**
  - `add-vscode-extension-host-evaluate` is applied and archived first, because this change renames keywords in its capability and changes the same files.
  - A later change keeps VS Code from writing to the user's home directory, with VS Code's portable mode.
- **Dependencies:** the libraries drop nothing they declare. The repository gets `@vscode/test-electron` and `electron` as npm development dependencies.
