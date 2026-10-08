# Tasks

## 1. Test setup and fixture app

- [x] 1.1 Add pytest as a dev dependency group in the root `pyproject.toml`, and create `packages/electron/atest/` for Robot suites and `packages/electron/tests/` for pytest. Verify that `uv sync` installs pytest and that `uv run pytest packages/electron/tests` and `uv run robot packages/electron/atest` both run (with an empty placeholder test).
- [x] 1.2 Write a Python helper (`packages/electron/atest/resources/ElectronFixture.py`) that downloads a pinned Electron release zip from GitHub, checks it against `SHASUMS256.txt`, extracts it into a gitignored cache and returns the executable path. Expose it as the keyword `Get Electron Executable`. Verify that the first call downloads, a second call uses the cache, and the returned path exists.
- [x] 1.3 Create the fixture app in `packages/electron/atest/fixtures/app/` (`package.json`, `main.js`, `index.html`):
  - a fixed window title,
  - a button that changes its own text,
  - a button that opens a second window with `window.open`,
  - quitting when all windows are closed,
  - a `--no-window` argument that starts the app without opening a window.

  Verify that it starts manually with the downloaded binary and that each behaviour works.
- [x] 1.4 Spike before building the hook: load a throwaway JavaScript module through Browser's `jsextension` that calls `playwright._electron.launch` on the fixture app and returns the first window's title. Verify that the title comes back. Keep the result in a short note in design.md; do not keep the code.

## 2. Browser hook (in `../robotframework-browser`, branch `adopt-context-hook`)

- [x] 2.1 Extract `PlaywrightState.adoptContext(context)` from `newPersistentContext`. It registers all existing pages with `_newPage`, makes the first page active and returns `{ browserId, contextId, pageId }`. Verify that the `New Persistent Context` acceptance tests still pass.
- [x] 2.2 Inject `adoptContext` in `extensionKeywordCall`, and add it to the reserved names in `call_js_keyword`. Verify with a Node unit test that an extension function receives a working `adoptContext`.
- [x] 2.3 Add an acceptance test: a JavaScript module adopts a context from `playwright.chromium.launchPersistentContext()`, then `Get Title` works and `Close Browser` ends the browser process. Verify that the test passes after `inv node-build`.
- [x] 2.4 Repeat the spike from 1.4 with `adoptContext`. Verify that `Get Title` and `Click` work on the fixture app's window through plain Browser keywords.
- [x] 2.5 Document `adoptContext` in the JavaScript-module section of the `Browser/browser.py` docs. Verify that libdoc renders the new paragraph.
- [x] 2.6 Draft the upstream issue or PR text that explains the hook and its use, and hand it to the user without posting it. Verify that the user has the text.
- [x] 2.7 Add the optional `onClose` argument to `adoptContext`: `BrowserState.close()` calls it once, even if closing the contexts failed. Cover it in the Jest tests and the acceptance test, document it, and update the upstream draft. Verify with `inv utest-node`, `inv atest --suite adopt_context` and `inv lint`.

## 3. Library skeleton

- [x] 3.1 Define `class Electron(Browser)` in `packages/electron/src/Electron/__init__.py`, with no own `__init__`. Set the intro to the own text followed by `Browser.__doc__`, and set `ROBOT_LIBRARY_VERSION` to the package version. Verify with pytest that `Library  Electron` imports, exposes all Browser keywords, converts `timeout=5s` and `auto_closing_level=SUITE`, and starts no Node process.
- [x] 3.2 Add a pytest check that libdoc of `Electron` reports the package version, has no unresolved links beyond Browser's own baseline, and starts no process. Verify that the test passes.

## 4. Starting applications

- [x] 4.1 Write `Electron/electron.js` with `robotframeworkElectronLaunch`: launch, wait for the first window within the timeout, then `adoptContext`; close the app if this fails. Make sure the package build includes it. Verify that it is present in the wheel built by `uv build`.
- [x] 4.2 Implement `New Electron Application`: executable check, lazy `init_js_extension`, `call_js_keyword`, and a return value shaped like that of `New Persistent Context`. Verify with Robot tests for the spec scenarios "Application opens a window", "Arguments and environment", "Test run started from inside VS Code", "Browser keywords act on the first window" and "Return value".
- [x] 4.3 Add Robot tests for "Second window", "Closing a window" and "Application and web browser". Verify that they pass.
- [x] 4.4 Add Robot tests for the failed-start scenarios "Wrong executable path" and "No window" (using `--no-window`), including that no app process remains. Verify that they pass.

## 5. Closing applications

- [x] 5.1 Implement `Close Electron Application    browser=CURRENT` through `close_browser`. Verify with Robot tests for "Close the active application", "Close by browser id" and "Application already exited", checking that the process has exited.
- [x] 5.2 Add Robot tests for Browser's closing paths: an app started in a test ends after the test, an app started in a suite setup ends after the suite, and `Close Context` ends the app. Verify that they pass.
- [x] 5.3 Write the keyword documentation and the README section: installation from the local Browser clone, `Electron` replaces `Browser`, Linux needs a display. Verify that libdoc shows both keywords with their documentation.

## 6. Electron.Helper

- [x] 6.1 Implement `Electron/Helper.py` with the library class `Helper` and `Get Electron Executable` (move the download logic out of the test helper, default to the user cache directory, add `cache_dir`). Verify with pytest: platform and executable mapping, cache reuse without a second download, a checksum mismatch that fails and leaves nothing in the cache, the error for an unknown version, and an `executable` that is returned unchanged.
- [x] 6.2 Switch the acceptance tests to `Electron.Helper` with the repository's `.cache/electron` as `cache_dir`, and keep only the fixture-specific keywords in `ElectronFixture.py`. Verify that all acceptance tests pass.
- [x] 6.3 Document the `Helper` library and its keyword, and add a README section. Verify that libdoc of `Electron.Helper` shows the keyword with its documentation and starts no Node process.
