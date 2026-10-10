# Proposal

## Why

A review of the libraries and their tests on 2026-10-10 found 15 issues. The most serious ones:
- **Paths:** relative paths and the default working directory refer to the folder of Browser's Node process, not to the test run.
- **Leaking processes:** a started application keeps running when Browser cannot take it over.
- **Archives:** extracting a downloaded archive can write files outside its folder.
- **No timeouts:** downloads and extension installs can hang forever.

The others are smaller errors, untidy test helpers, and avoidable work and network access.

## What Changes

- **Paths:** `New Electron Application` resolves a relative executable and working directory against the test run's working directory, and runs the application there when no working directory is given.
- **Failed start:**
  - If Browser cannot take over a started application, for example because it has no `adoptContext` hook, the application is closed, and the error says why.
  - An application whose first window closes during the start no longer fails with a `KeyError`.
- **Downloads:**
  - Extracting refuses archive entries outside the target folder, also for tar archives on Python versions before 3.12.
  - Network requests time out.
  - Unsupported processor architectures fail with an error instead of downloading an x64 build.
  - `stable` and `insiders` are looked up once per process, and offline the newest cached build of that quality is used.
- **VS Code:**
  - `Open VS Code` resolves an executable on `PATH` or behind a symlink, so that it finds the command-line script and the version.
  - A failing cleanup no longer hides the error of a start that did not finish.
  - Installing extensions times out, and all `extensions` are installed with one call of the command-line script.
  - `Install VS Code Extension` fails for an instance that has been closed.
- **Internals and tests:**
  - The Electron download hashes the archive while streaming and shares its download steps with the VS Code download.
  - The test fixtures escape the paths they pass to `pgrep`.

None of the changes needs a change to the Browser library.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: paths and working directory, cleanup when Browser cannot take over an application, a first window that closes.
- `electron-download`: safe extraction, timeouts, unsupported architectures.
- `vscode-download`: the same, and how `stable` and `insiders` are resolved.
- `vscode-launch`: executables on `PATH` or behind a symlink, errors of an unfinished start, timeouts for extensions, closed instances.

## Impact

- `packages/electron/src/Electron/__init__.py`, `electron.js` and `Helper.py`, `packages/vscode/src/VSCode/__init__.py`, `download.py` and `instance.py`.
- Unit tests in both packages, acceptance tests for the working directory and relative paths, and the test fixtures.
