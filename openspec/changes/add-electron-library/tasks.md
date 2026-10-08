# Tasks

## 1. Browser hook (in `../robotframework-browser`, branch `adopt-context-hook`)

- [ ] 1.1 Extract `PlaywrightState.adoptContext(context)` from `newPersistentContext`. Register all existing pages with `_newPage`, make the first page active, and return `{ browserId, contextId, pageId }`. Verify that `New Persistent Context` acceptance tests still pass.
- [ ] 1.2 Inject `adoptContext` in `extensionKeywordCall`, and add it to the reserved names in `call_js_keyword`. Verify with a Node unit test that an extension function receives a working `adoptContext`.
- [ ] 1.3 Add an acceptance test: a JavaScript module adopts a context from `playwright.chromium.launchPersistentContext()`, then `Get Title` works and `Close Browser` ends the browser process. Verify that the test passes after `inv node-build`.
- [ ] 1.4 Document `adoptContext` in the JavaScript-module section of the `Browser/browser.py` docs. Verify that libdoc renders the new paragraph.
- [ ] 1.5 Draft the upstream issue or PR text explaining the hook and its use, and hand it to the user (do not post it). Verify that the user has the text.

## 2. Library skeleton

- [ ] 2.1 Define `class Electron(Browser)` in `packages/electron/src/Electron/__init__.py`, with no own `__init__`. Set the intro to the own text followed by `Browser.__doc__`, and set `ROBOT_LIBRARY_VERSION` to the package version. Verify with pytest that `Library  Electron` imports, exposes all Browser keywords, converts `timeout=5s` and `auto_closing_level=SUITE`, and starts no Node process.
- [ ] 2.2 Add a pytest check that libdoc of `Electron` reports the package version, has no unresolved links beyond Browser's own baseline, and starts no process. Verify that the test passes.
- [ ] 2.3 Add pytest as a dev dependency group in the root `pyproject.toml`. Verify that `uv sync` installs it and `uv run pytest` runs the new tests.

## 3. Test fixture

- [ ] 3.1 Create the fixture app in `packages/electron/atest/fixtures/app/` (`package.json`, `main.js`, `index.html`) with a fixed title, a button that changes text, and a button that opens a second window. Verify that it starts manually with the downloaded Electron binary.
- [ ] 3.2 Write a Python helper for the tests that downloads a pinned Electron release zip from GitHub into a gitignored cache and returns the executable path. Verify that a second call uses the cache.

## 4. Starting applications

- [ ] 4.1 Write `Electron/electron.js` with `robotframeworkElectronLaunch` (launch, wait for the first window with the timeout, `adoptContext`; close the app on failure). Make sure the package build includes it. Verify that it is present in the wheel built by `uv build`.
- [ ] 4.2 Implement `New Electron Application` (executable check, lazy `init_js_extension`, `call_js_keyword`, return value shaped like `New Persistent Context`). Verify with Robot tests for the spec scenarios "Application opens a window", "Arguments and environment", "Browser keywords act on the first window" and "Return value".
- [ ] 4.3 Add Robot tests for "Second window", "Closing a window" and "Application and web browser". Verify that they pass.
- [ ] 4.4 Add Robot tests for the failed-start scenarios "Wrong executable path" and "No window" (using a fixture argument that suppresses the window), including that no app process remains. Verify that they pass.

## 5. Closing applications

- [ ] 5.1 Implement `Close Electron Application    browser=CURRENT` through `close_browser`. Verify with Robot tests for "Close the active application", "Close by browser id" and "Application already exited", checking that the process has exited.
- [ ] 5.2 Add Robot tests for Browser's closing paths: the app started in a test ends after the test, the app started in a suite setup ends after the suite, and `Close Context` ends the app. Verify that they pass.
- [ ] 5.3 Write the keyword documentation and the README section (installation from the local Browser clone, `Electron` replaces `Browser`, Linux needs a display). Verify that libdoc shows both keywords with their documentation.
