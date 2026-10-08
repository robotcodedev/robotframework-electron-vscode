# Tasks

## 1. Library skeleton

- [x] 1.1 Define `class VSCode(Electron)` in `packages/vscode/src/VSCode/__init__.py`, with no own `__init__`. Set the intro to the own text followed by `Electron.__doc__`, and set `ROBOT_LIBRARY_VERSION` to the package version. Verify with pytest that `Library  VSCode` exposes the Browser and Electron keywords, reports its own version in libdoc and starts no process on import.
- [x] 1.2 Set up the tests:
  - `packages/vscode/tests/` for pytest and `packages/vscode/atest/` for Robot.
  - An `__init__.robot` with `Name    VSCode` in `packages/vscode/atest/` and one with `Name    Electron` in `packages/electron/atest/`.
  - `packages/vscode/atest` added to the `robot.toml` paths.
  - A resource with `${VSCODE_VERSION}`, `${VSCODE_EXECUTABLE}` and `${VSCODE_CACHE}`.
  - The profile `vscode-insiders`.

  Verify with `robotcode discover suites` that both suites appear under their names, and that the Electron tests still pass.

## 2. Downloading VS Code

- [x] 2.1 Implement platform detection and version resolution against the update service in `VSCode/download.py` (`/api/update/.../latest` for stable and insiders, `/api/versions/<version>/...` for fixed versions). Verify with pytest against faked service answers (stable, insiders, fixed version, unknown version).
- [x] 2.2 Implement download, checksum check, extraction into a temporary folder and the atomic move into the cache. Verify with pytest that a second call does not download, that a checksum mismatch or an interrupted download leaves nothing usable in the cache, and that two concurrent calls return the same path.
- [x] 2.3 Implement executable and CLI path lookup per platform and quality. Verify with pytest against the layouts of `@vscode/test-electron`, and on Linux with a real `Download VS Code    stable`.
- [x] 2.4 Add the `Download VS Code    version=stable    cache_dir=${NONE}` keyword with docs. Verify with a Robot test that it returns an existing executable path.

## 3. Test extension

- [x] 3.1 Create `packages/vscode/atest/fixtures/extension/` (`package.json`, `extension.js`) with the command `Robot Test: Say Hello`, which shows a notification. Verify by starting VS Code manually with `--extensionDevelopmentPath` and running the command.

## 4. Opening and closing VS Code

- [x] 4.1 Implement the instance directories under `${OUTPUT DIR}/vscode/<n>/`, settings defaults and merge, the environment without `VSCODE_*`, and the launch arguments. Verify with pytest that the argument and settings builder produces the expected values.
- [x] 4.2 Implement `Open VS Code` (version or executable path, extension folders, folder or file, extra args, timeout) on top of `New Electron Application`. Make it wait for the workbench and store the product version. Verify with Robot tests for "Workbench is ready", "Local installation", "Development extension is active" and "Folder".
- [x] 4.3 Install dependency extensions through the CLI before the start. Verify with a Robot test for "Marketplace extension", including that the user's own extensions directory is untouched.
- [x] 4.4 Add Robot tests for "Setting takes effect", "Quiet start", "Two instances", "User's VS Code is unaffected" and "Logs after a failed test". Verify that they pass.
- [x] 4.5 Implement `Close VS Code` on top of `Close Electron Application`. Verify with a Robot test that the process has exited when the keyword returns.
- [x] 4.6 Write the keyword docs and the README section (quick start, cache, Linux display and sandbox notes). Verify that libdoc shows all three keywords and that the README example runs as written.
