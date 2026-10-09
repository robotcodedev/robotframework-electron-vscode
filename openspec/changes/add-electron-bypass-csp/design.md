# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements.
- **Playwright:** `bypassCSP` is a context option, and `_electron.launch` accepts it like other context options. Playwright makes Chromium ignore the page's Content Security Policy, which includes `require-trusted-types-for`.
- **Test of 2026-10-09:** VS Code 1.141 started through `_electron.launch`.
  - Without the option, `page.addScriptTag` failed for an inline classic script, an inline module and Browser's `selector-finder.js`, each with the Trusted Types error.
  - With `bypassCSP: true`, all three were added and ran.
- **Microsoft's smoke tests:** they do not bypass the policy. They start VS Code with `--enable-smoke-test-driver` and call VS Code's own test driver through `page.evaluate`, which the policy does not restrict.

## Goals / Non-Goals

**Goals:**
- The same option as Browser's `bypassCSP` of `New Context`, for Electron applications and VS Code.

**Non-Goals:**
- Turning it on by default. It also applies to webviews and other frames, and a test would then miss CSP problems of the application or the extension under test.
- Fixing Browser's presenter mode, which falls back to the selector recorder when it cannot highlight an element. That is a matter of the Browser library.

## Decisions

### Argument

- `New Electron Application` gets `bypass_csp: bool = False`, after `record_video`.
- `electron.js` adds `bypassCSP` to the options of `_electron.launch` only when it is true, so that the default launch stays exactly as before.
- `Open VS Code` gets the same argument and passes it on.
- The keyword documentation names `Record Selector` as the main use, and warns about webviews.

### Fixture and tests

- **Fixture:** the fixture app gets a page `csp.html` with the policy `default-src 'self'; script-src 'self'; require-trusted-types-for 'script'`. The app loads it instead of `index.html` when it gets the argument `--page=csp.html`.
- **Test of a script element:** a script element with inline code is added through `Evaluate JavaScript`. With Trusted Types required, setting the element's `text` throws, so the test sees an error without the option and the script's effect with it. `Evaluate JavaScript` itself runs through the DevTools protocol and is not restricted by the policy.
- **Electron:** two acceptance tests with the fixture page, one with and one without `bypass_csp`.
- **VS Code:** one acceptance test with the workbench and `bypass_csp=True`.

### Documentation

- **Browser features guide:** a row for `Record Selector`, which needs `bypass_csp` in VS Code.
- **Getting started for Electron:** a sentence on the option.

## Risks / Trade-offs

- [Users switch it on everywhere] → The keyword documentation and the guide say that it also disables the policy of webviews, and recommend it only where a feature needs it.
- [A Playwright release drops `bypassCSP` for Electron] → The acceptance tests would show it at once.
