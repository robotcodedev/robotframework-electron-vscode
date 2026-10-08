# Design

## Context

See proposal.md for motivation and specs/electron-applications/spec.md for the required behaviour.

The Browser library keeps its state (browsers, contexts, pages) in its Node process (`PlaywrightState` in `node/playwright-wrapper/playwright-state.ts`). JavaScript extension functions get injected parameters by name (`page`, `context`, `browser`, `logger`, `playwright`, in `extensionKeywordCall`). None of them can register a context the function created itself. `newPersistentContext` already does this internally for a context without a browser: it creates a `BrowserState` with `browser: null`, wraps the context with `_createIndexedContext` and registers the first page with `_newPage`.

Playwright 1.63 gives an Electron app's context a custom close handler. `context.close()` calls `app.quit()` in the main process and waits until the process has exited. Closing a page closes its window through `webContents.close()`. All of Browser's closing paths call `context.close()`, so they end the app without extra code.

## Goals / Non-Goals

**Goals:**
- A small, generic upstream hook. The hook carries no Electron knowledge.
- A thin `Electron` library: one JavaScript function plus two keywords on top of Browser.

**Non-Goals:**
- Access to the Electron main process (`app.evaluate`), tracing or video for apps. These can come later.
- The CDP fallback (`--remote-debugging-port` plus `Connect To Browser`).
- CI. It is deferred until the hook is released.

## Decisions

### Hook: `adoptContext`, extracted from `newPersistentContext`

In the Browser clone (`../robotframework-browser`, branch `adopt-context-hook`):
- `PlaywrightState.adoptContext(context)` creates a `BrowserState` with `browser: null` and pushes it as the active browser. It wraps the context with `_createIndexedContext`, registers every existing page with `_newPage` (so closed windows leave the page stack) and makes the first page active. It returns `{ browserId, contextId, pageId }`.
- `newPersistentContext` is refactored to use the helper. This makes the PR mostly a refactoring.
- `extensionKeywordCall` injects `adoptContext` like `playwright`. `call_js_keyword` in `Browser/browser.py` adds `adoptContext` to its reserved names, and the JavaScript-module section of the Browser docs documents the new parameter.
- `adoptContext(context, onClose)` takes an optional async `onClose`. `BrowserState.close()` calls it exactly once, after the contexts are closed, even if closing them failed. Electron does not need it, because closing the context already quits the app. Other creators do: an Android device connection, for example, stays open after its browser context is closed. With `onClose` the hook covers more than Electron, which makes it a more general proposal upstream.
- Upstream acceptance test: a JavaScript module adopts a context from `playwright.chromium.launchPersistentContext()`. Then `Get Title` works, and `Close Browser` ends the browser process. This needs no Electron in Browser's CI.

Alternative considered: extracting the helper from `addBrowser`. That function registers existing pages with `indexedPage()` only, so pages closed by the app would stay in the stack.

### Library: `class Electron(Browser)` with keyword methods

- `packages/electron/src/Electron/__init__.py` defines `class Electron(Browser)`, so `Library  Electron` works.
- No own `__init__`, so Robot Framework uses Browser's signature, type conversion and import docs unchanged. If state is ever needed in `__init__`, use `@functools.wraps(Browser.__init__)` and never a bare `*args, **kwargs` passthrough.
- The class docstring is the library's own intro followed by `Browser.__doc__` (both `inspect.cleandoc`-ed), so the links in Browser's keyword docs keep working. `ROBOT_LIBRARY_VERSION` is the package version.
- `New Electron Application` and `Close Electron Application` are `@keyword` methods on the class. They run through Browser's `run_keyword`, so they get run-on-failure and the keyword banner.
- Listener extensions, if needed, override Browser's underscore methods and call `super()`.

### Launch through a lazily loaded JavaScript module

- `Electron/electron.js` exports a single, distinctively named function, `robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, playwright, adoptContext)`. It calls `playwright._electron.launch`, then `app.firstWindow({ timeout })`, then `adoptContext(app.context())`. If the first window fails to appear, it closes the app before rethrowing.
- The Python keyword loads the module with `self.init_js_extension()` on first use, once per library instance, and calls it with `self.call_js_keyword()`. Nothing happens at import.
- Before calling Node, the Python keyword checks that the executable exists (as a file, or as a command on `PATH`) and fails with a message that names the path.
- Arguments: `executable_path`, `args`, `env`, `cwd` and `timeout` (default: the library timeout).
- Environment: a given `env` is passed unchanged, which matches `New Browser`. Without `env`, the keyword passes a copy of `os.environ` without `ELECTRON_RUN_AS_NODE`. Test runs started from VS Code inherit that variable, and it would make every Electron binary run as plain Node (see the spike result below).
- The return value is built from the hook's ids as `(browser_id, context_id, NewPageDetails(page_id, None))`, the same shape `New Persistent Context` returns.

### Closing through `Close Browser`

`Close Electron Application    browser=CURRENT` calls `self.close_browser(browser)`. The Node side awaits `context.close()`, so the keyword returns after the app has exited. `closeBrowser` already treats an app that is already gone as success.

### `Electron.Helper`: downloading Electron

- `Electron/Helper.py` contains a plain Robot Framework library class `Helper`, imported as `Library    Electron.Helper`. It has no Browser state, so it starts no Node process and works without an open browser.
- `Get Electron Executable    version    executable=None    cache_dir=None`:
  - It downloads `electron-v<version>-<platform>-<arch>.zip` from the GitHub release, checks it against the release's `SHASUMS256.txt`, extracts it into a temporary folder in the cache, and moves the folder into place with `os.replace`. A folder in the cache therefore only exists once it is complete.
  - Extraction restores file modes and symlinks, which `zipfile` drops; the macOS framework bundle needs the symlinks.
  - A given `executable` is returned unchanged.
- The cache defaults to the user's cache directory: `$XDG_CACHE_HOME` or `~/.cache` on Linux, `~/Library/Caches` on macOS, `%LOCALAPPDATA%` on Windows, each with `robotframework-electron/electron` appended.
- The standard library is enough (`urllib`, `zipfile`, `hashlib`), so there is no new dependency.
- The tests keep the version as test data in `${ELECTRON_VERSION}`. They use the repository's gitignored `.cache/electron` as `cache_dir`, and can switch to a local binary with `--variable ELECTRON_EXECUTABLE:...`.

### Fixture app for tests

- Tests use a minimal Electron app in `packages/electron/atest/fixtures/app/` (`package.json`, `main.js`, `index.html`). It has a fixed title, a button that changes text, a button that opens a second window, and a `--no-window` argument for the failed-start test.
- The Electron binary comes from `Electron.Helper`'s `Get Electron Executable`, so no npm is involved. The test helper `atest/resources/ElectronFixture.py` only provides the fixture app path and a process counter.
- Tests are Robot suites in `packages/electron/atest/` and pytest checks for import and libdoc in `packages/electron/tests/`.
- The fixture app and test setup come first. A spike runs `_electron.launch` against the fixture through a throwaway JavaScript module before the hook is built.

Spike result (2026-10-08, Electron 44.7.0, Playwright 1.63, under `xvfb-run -a`):
- A JavaScript module loaded with `jsextension=` launched the fixture app through `playwright._electron.launch`, got the first window and its title, and closed the app. The plain Playwright checks confirmed the rest: a click changes the button text, `window.open` adds a second page to the app's context, closing that page closes the window, and after `app.close()` the process is gone.
- With `--no-window`, `firstWindow({ timeout })` raises a `TimeoutError`.
- Finding: a process started from inside VS Code (an integrated terminal, or an extension such as RobotCode running tests) inherits `ELECTRON_RUN_AS_NODE=1`. Every Electron binary started with that environment runs as plain Node and fails with "Cannot find module 'electron'", and Playwright reports "Process failed to launch!".

## Risks / Trade-offs

- [Playwright marks `_electron` as experimental] → Pin through Browser's Playwright version and keep the JavaScript module small, so changes stay local.
- [The hook is not accepted upstream, or only in another shape] → The library uses the hook only inside `electron.js`, so another shape means changing one function. Agree on the shape with the maintainer before polishing.
- [Apps whose Node inspector is disabled (Electron fuse `EnableNodeCliInspectArguments`) cannot be launched by Playwright] → Document it. The CDP fallback stays a possible later addition.
- [Users import `Browser` and `Electron` together] → Document that `Electron` replaces `Browser`, and point to the usual Robot Framework patterns.
- [The JavaScript-module call has no Browser timeout context, so the adopted context gets Playwright's default timeouts] → Browser keywords pass their own timeouts. Revisit if a keyword turns out to rely on the context default.
