# Tasks

## 1. Test first

- [x] 1.1 Add "Browser Keywords Act On The First Window With Views" to `start_application.robot`. Verify that it fails with `-p xvfb` before the fix, and note how it fails.

## 2. Fix

- [x] 2.1 Add the window-page check to `electron.js`, the wait for a window page in the launch, the video path of that page, and `robotframeworkElectronIsWindowPage`. Add unit tests in `test_electron_js.py`. Verify that `uv run pytest` passes.
- [x] 2.2 Switch to the window page in `New Electron Application` when the active page is not one, and return its page id. Add unit tests in `test_library.py`. Verify that the test of 1.1 passes five times in a row with `-p xvfb`, and that all Electron acceptance tests pass.

## 3. Cleanup

- [x] 3.1 Remove the switch by title from the `>>>` test in `pages.robot`. Verify that the VSCode acceptance tests and `uv run pre-commit run --all-files` pass.
