# Tasks

## 1. Electron applications

- [x] 1.1 Resolve a relative executable and working directory against the test run's working directory, and default the working directory to it. Add acceptance tests for the default working directory and a relative executable path.
- [x] 1.2 Close the application in `electron.js` when anything after the launch fails, and report a Browser library without the `adoptContext` hook before the launch. Add a unit test that runs `electron.js` with Node and fakes for Playwright and the hook.
- [x] 1.3 Read `pageId` with a default, so that a first window that closes during the start does not fail the keyword. Add a unit test.

## 2. Downloads

- [x] 2.1 Move `open_url` with a timeout, a streaming `sha256` and the download step into `Electron.Helper`, and use them in both downloads.
- [x] 2.2 Check every archive entry and symlink target against the target folder, for zip and tar archives, and create symlinks after the files. Add unit tests with malicious archives.
- [x] 2.3 Reject unsupported processor architectures in both platform functions. Add unit tests.
- [x] 2.4 Look up `stable` and `insiders` once per process, and fall back to the newest cached build of that quality when the update service cannot be reached. Add unit tests.

## 3. VS Code

- [x] 3.1 Resolve the executable of `Open VS Code` through `PATH` and symlinks. Add unit tests for the resolution.
- [x] 3.2 Install all `extensions` with one call of the command-line script, with a timeout of 10 minutes. Add unit tests for the arguments and the timeout.
- [x] 3.3 Keep the original error when the workbench does not become ready and closing fails.
- [x] 3.4 Let `Install VS Code Extension` fail for a closed instance, and drop closed instances from the registry. Add an acceptance test.

## 4. Test fixtures and verification

- [x] 4.1 Escape the paths given to `pgrep -f` in both test fixtures.
- [x] 4.2 Verify that `uv run pytest`, `uv run pre-commit run --all-files` and the acceptance tests pass.
