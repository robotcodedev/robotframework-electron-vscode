# Draft: upstream proposal for `adoptContext`

Draft text for an issue or pull request in MarketSquare/robotframework-browser. It is not posted yet. The code is on the branch `adopt-context-hook` of the local clone.

---

## Let JavaScript extensions hand a self-created context to Browser

### Problem

A JavaScript extension can create a `BrowserContext` itself, for example with `playwright._electron.launch()`, `playwright.chromium.launchPersistentContext()` with special options, or `playwright._android`. Browser keywords cannot use that context, though. An extension function receives `page`, `context`, `browser`, `logger` and `playwright`, but it has no way to register a new context in the library's state. The context stays invisible to `Click`, `Get Text`, `Close Browser` and auto-closing.

This is what blocks Electron support (#4925, #4695). It also blocks any other special launch that Browser itself does not cover.

### Proposal

One more injected argument for extension functions: `adoptContext`.

```js
async function launchMyApp(executablePath, playwright, adoptContext) {
    const app = await playwright._electron.launch({ executablePath });
    await app.firstWindow();
    return adoptContext(app.context()); // { browserId, contextId, pageId }
}
```

`adoptContext(context, onClose)` adds the context as a new active browser without a browser object, in the same way `New Persistent Context` does. Its existing pages become pages of that context, and the first page becomes the active page. Closing the browser closes the context, through `Close Browser`, auto-closing or the end of the run. For an Electron app, Playwright's own close handler then quits the app.

The optional async `onClose` runs once after the context is closed, even if closing it failed. It lets the function release what the context does not own. An Android device connection is one example:

```js
async function newAndroidChrome(playwright, adoptContext) {
    const [device] = await playwright._android.devices();
    const context = await device.launchBrowser();
    return adoptContext(context, () => device.close());
}
```

Electron-specific keywords would live in a separate library built on Browser. Browser itself gets no Electron code, no new keyword and no protobuf change, and its CI needs no Electron.

### Change

- `PlaywrightState.adoptContext(context, onClose)` uses a helper, `_indexContextWithPages`, extracted from `newPersistentContext`, so `newPersistentContext` uses the same code path. One side effect: `newPersistentContext` now registers every page the context already has, not only the first. Its response still reports the first page.
- `BrowserState` gets an optional `onClose`. `BrowserState.close()` calls it once in a `finally` block, after closing the contexts and the browser.
- `extensionKeywordCall` injects `adoptContext`.
- On the Python side, the injected argument names are one class attribute, `Browser._js_injected_arguments`, used both when keywords are built from JavaScript extensions and in `call_js_keyword`. `adoptContext` is added to it.
- The `jsextension` import argument documentation describes `adoptContext`.

### Tests

- Jest (`playwright-state.test.ts`):
  - `adoptContext` adds a new active browser with a `null` browser object.
  - It registers all existing pages and activates the first.
  - Two adoptions stay separate browsers.
  - `onClose` runs exactly once, even if the browser state is closed twice.
  - `onClose` runs even if closing the context fails.
  - An extension function receives a working `adoptContext`.
- Acceptance test (`atest/test/05_JS_Tests/adopt_context.robot`): an extension opens `chromium.launchPersistentContext()` and adopts it. `Get Text` works on its page, and `Close Browser` closes the context and calls `onClose`.
- The existing persistent-context and JavaScript-extension suites still pass.

### Compatibility

An existing extension function with a parameter named `adoptContext` would now receive the library's function instead of the keyword argument. The name was chosen to make that unlikely.
