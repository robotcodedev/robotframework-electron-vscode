# Background and Initial Design Ideas

Collected on 2026-10-07 while discussing tests for the RobotCode VS Code extension. This is starting material for planning (`/opsx:explore`), not a decided design. Code references to the Browser library point at commit `2cf74ae6` of `MarketSquare/robotframework-browser` (`main`, release 20.6.0).

## Goal

Write end-to-end UI tests for VS Code extensions in Robot Framework, using the Browser library, instead of Playwright test code in TypeScript. Publish the result for other extension developers.

Decisions so far:

- Two libraries in this repository:
  - `robotframework-electron` (`Electron`): starts Electron applications and hands their windows to the Browser library.
  - `robotframework-vscode` (`VSCode`): generic VS Code layer for any extension developer.
- RobotCode-specific keywords and the RobotCode tests themselves stay in the RobotCode repository.
- Electron support is **not** built into the Browser library. Upstream only gets one small, generic hook (see below).
- Until the hook is released, the Browser library comes from a local clone at `~/develop/robot/robotframework-browser` (`../robotframework-browser` from this repository), used as an editable path dependency.
  - The hook is developed there on the branch `adopt-context-hook`, created from `main` at `2cf74ae6`.
  - It is only a local clone so far: `origin` is `MarketSquare/robotframework-browser`, and there is no GitHub fork.
  - How to prepare the clone is described in [AGENTS.md](../AGENTS.md).
- Do not model the design on Browser PR #4695 ("Add Electron application support"). It is AI-generated, stalled since 2026-03 and has open maintainer remarks.

## Where This Fits in RobotCode's Test Layers

The RobotCode extension currently has no tests of its own. The intended layers:

1. Unit tests with Vitest for pure logic: the Documentation Viewer webview (`matcher.ts`, `find.ts`, `page.ts`) and `utils.ts`.
2. Integration tests with `@vscode/test-electron` / `@vscode/test-cli`. They run inside the extension host with the full `vscode` API, but cannot see the UI.
3. Component tests of the Documentation Viewer webview in a plain browser. The webview only talks through `acquireVsCodeApi().postMessage` and `message` events (typed in `protocol.ts`), so it can run in a test page with a stub. This works with the Browser library today.
4. A few end-to-end tests in a real VS Code. This repository is for this layer.

Layers 1–3 are planned in the RobotCode repository.

## Why xvfb

VS Code is an Electron app (Chromium with a real window) and has no headless mode. On Linux it needs a display server, and CI runners have none, so VS Code is run under `xvfb-run -a`. This applies to `@vscode/test-electron` and to UI automation alike. Windows and macOS runners have a desktop session and need nothing extra.

## Existing Tools and Experience

- **`@vscode/test-electron` / `@vscode/test-cli`** (Microsoft): the official way. Tests run inside the extension host, are stable, and see no UI.
- **Playwright `_electron`**: drives the VS Code UI from outside. Playwright marks Electron support as experimental.
  - VS Code's own smoke tests use it: `test/automation/src/playwrightElectron.ts` calls `playwrightImpl._electron.launch(...)`.
  - Salesforce (`forcedotcom/salesforcedx-vscode`, package `playwright-vscode-ext`) uses `_electron.launch` together with `downloadAndUnzipVSCode` from `@vscode/test-electron`. They have about 150 spec files and CI on macOS, Ubuntu (with `xvfb-run -a`) and Windows. They configure 2 retries and `maxFailures: 3` in CI, and rerun failed tests with `--last-failed`. It works at scale, but not without flakiness.
  - Playwright declined a dedicated VS Code target (microsoft/playwright#22351, closed as "not planned").
- **ExTester** (`redhat-developer/vscode-extension-tester`, Selenium-based): very active (v8.28.1 on 2026-10-05). It ships page objects per VS Code version, including webviews. Used for example by HashiCorp Terraform, Docker, Continue, Espressif, Azure Logic Apps, Apache KIE and Google Colab.
- **wdio-vscode-service** (WebdriverIO): version-aware locators, plus `executeWorkbench` to run code with the `vscode` API from a test. Less active (last release 2025-09).
- RobotCode's own isolated harness (Playwright `_electron` + xvfb, own profile, `VSCODE_*` stripped) ran the Documentation Viewer checks 32/32 on VS Code 1.127 and 1.140. Quirks seen: the preview frame is swapped when the theme changes.

## Browser Library: How It Can Be Extended

From `docs/plugins/README.md` and the code there are three ways:

- **Python plugins** (`plugins=`): classes deriving from `LibraryComponent`.
  - They can add or override keywords and change Python-side internals.
  - `self.library` gives the whole Browser instance.
  - A plugin can load a JS module with `initialize_js_extension()` and call it with `call_js_keyword()` (`Browser/base/librarycomponent.py:218`, `:223`).
- **JS modules** (`jsextension=`, or loaded by a plugin): `extensionKeywordCall` (`node/playwright-wrapper/playwright-state.ts:156`) fills function parameters by name: `page`, `context`, `browser`, `logger`, `playwright`. With `playwright` a module can call `playwright._electron.launch()`. `page` and `context` are simply undefined when no browser is open.
- **New libraries** built on top of Browser.

The state (browsers, contexts, pages) lives in the Node process (`PlaywrightState`). Python reaches it only through the gRPC methods in the proto; JS modules reach it only through the injected parameters above. **Neither way can register a context that the module created itself.** Without that, `Click`, `Get Text`, etc. do not work on the windows of an app launched by a module.

Relevant facts of the state model:

- **Context without a browser.** `BrowserState` with `browser: null` already exists: `newPersistentContext` (`:956`) uses it. An Electron app has the same shape: `electronApp.context()` is the context and the windows are its pages.
- **Adopting existing contexts.** `addBrowser` (`:486`) adopts the existing contexts and pages of a browser, used after `connectOverCDP`, and listens for new pages.
- **Closing.** `BrowserState.close()` (`:656`) closes all contexts and then the browser if there is one. `closeContext` (`:777`) closes a `browser: null` state when its last context is gone. Python auto-closing (`_prune_execution_stack`, `Browser/browser.py:1185`) compares the Node-side catalog before and after a test or suite and closes new contexts through Node.
- **Batteries.** If `robotframework-browser-batteries` is installed, its own gRPC server is used (`batteries_grpc_server`, `Browser/playwright.py:83`). A patched Node part in a clone is then silently bypassed.

Upstream status: there is no Electron support. PR #4695 is open and stalled; issue #4925 is open.

## The Hook (Proposal for Upstream)

One generic hook: JS modules get a function that hands a self-created `BrowserContext` to the library, with an optional owner-supplied close. A sketch, not an existing API:

```ts
// BrowserAndConfs / BrowserState: optional close hook
onClose?: () => Promise<void>;
// in BrowserState.close(), for browser === null:
await this.onClose?.();

// PlaywrightState: adopt an existing context (helper extracted from addBrowser)
public adoptContext(context: BrowserContext, onClose?: () => Promise<void>): BrowserState { ... }

// extensionKeywordCall: offer it as an injectable parameter
apiArguments.set('adoptContext', (context, onClose) => state.adoptContext(context, onClose).id);
```

The JS module of the Electron library would then be:

```js
async function launchElectron(executablePath, args, playwright, adoptContext) {
  const app = await playwright._electron.launch({ executablePath, args });
  await app.firstWindow();
  return adoptContext(app.context(), () => app.close());
}
```

Why this should be easier to get merged than full Electron support:

- **Not Electron-specific.** It works for any context a module creates: Electron, `_android`, special launches.
- **Small.** No new keyword and no proto or gRPC change; the main work is extracting the context-wrapping part of `addBrowser` into a helper.
- **Testable without Electron.** An acceptance test can use a JS module that launches `playwright.chromium` and adopts its context. The maintainers need no Electron knowledge and no Electron in their CI.

The parameter name becomes public API of JS modules and must be documented in the JS-module section of `Browser/browser.py`.

Open questions:

- Does `context.close()` on an Electron app's context end the app, or must the owner close replace the default `context.close()`?
- How do multiple windows behave, for example a new VS Code window?
- Naming and shape of the hook. Agree on it with the maintainer (Tatu Aalto) early.

User-facing keywords stay in our library: `New Electron Application` and `Close Electron Application`. The latter can simply call `close_browser(<id>)`, so all closing paths (explicit, `Close Browser`, auto-closing, end of run) end the app through the hook.

## Fallback Without the Hook: CDP

This works with today's Browser release:

1. Start the app with `--remote-debugging-port` and wait for "DevTools listening on ws://…" on stderr.
2. Call `Connect To Browser    <url>    chromium    use_cdp=True` (`connect_to_browser`, `Browser/keywords/playwright_state.py:409`). `addBrowser` adopts the open windows as pages.

Our library then owns the process. It can register as an RF listener and end apps at the end of the test or suite that started them. There is no access to the Electron main process. Not tried with VS Code yet.

## VS Code Library: Design Considerations

- **Selectors are the main cost.** The workbench DOM is not an API, and VS Code releases weekly.
  - Prefer commands and keybindings over DOM clicks, and ARIA roles and labels over CSS classes.
  - Keep all selectors in one place, overridable per VS Code version.
  - VS Code's own `test/automation` drivers (`quickaccess.ts`, `editor.ts`, `explorer.ts`, …) solve the same problem and are kept current by Microsoft; use them as a reference when VS Code changes.
- **Webviews:** provide a selector prefix (nested iframes, `>>>`) so all Browser keywords work inside webviews, instead of separate webview keywords.
- **Launch:**
  - Download and cache VS Code (fixed versions, stable, insiders) in Python, as `@vscode/test-electron` does, so users need nothing from npm beyond the Browser library itself.
  - Isolated launch: own user-data and extensions directories, `VSCODE_*` variables removed from the environment, the extension under test via `--extensionDevelopmentPath`, preinstalled dependency extensions, preset settings.
- **CI of the library:** regular runs against stable, insiders and the oldest supported version.
- **Option for later:** API access from tests, like wdio-vscode-service's `executeWorkbench`, for example through a small helper extension installed by the library.

## Open Decisions

- Electron layer as a Browser plugin (`Library  Browser  plugins=…`) or as a standalone library. Leaning towards a plugin: it is the documented extension way and brings `self.library` and `initialize_js_extension`.
- VS Code layer as a standalone library with its own namespace (`Library  VSCode`). Leaning towards yes.
- CI for the end-to-end tests: not decided. If yes, the Browser clone must exist there at the same relative path, either cloned and prepared in the job or as a git submodule.
- License.
