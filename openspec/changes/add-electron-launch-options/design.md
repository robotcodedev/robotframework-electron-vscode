# Design

## Context

See proposal.md for the motivation and the spec deltas for the requirements.

- **Playwright 1.63:** `_electron.launch` accepts `colorScheme` (`light`, `dark`, `no-preference` or `null`, default `light`), `locale`, `timezoneId` and `bypassCSP` (protocol `ElectronLaunchParams`). They are options of the application's one context and apply to its pages. The main process is not affected: `app.getLocale()` and Node's time zone follow the system, `--lang` and `TZ`.
- **Our launch today:** `electron.js` builds `contextOptions` (`acceptDownloads`, `recordVideo`, `recordHar`), passes them to `_electron.launch` and hands them to Browser's `adoptContext`, which keeps them with the context.
- **Earlier tests:**
  - Keyword audit, 2026-10-10:
    - Without `colorScheme`, a page of an application with `nativeTheme.themeSource = 'dark'` matched `prefers-color-scheme: light`. With `colorScheme: null`, it matched `dark`.
    - `locale` and `timezoneId` set `navigator.language`, number formatting and the time zone of the pages. `--lang` set only `navigator.language`.
  - Test of 2026-10-09: VS Code 1.141 started through `_electron.launch`.
    - Without `bypassCSP`, `page.addScriptTag` failed with the Trusted Types error for an inline classic script, an inline module and Browser's `selector-finder.js`.
    - With `bypassCSP: true`, all three were added and ran.
- **Microsoft's smoke tests:** they do not bypass the policy. They start VS Code with `--enable-smoke-test-driver` and call VS Code's own test driver through `page.evaluate`, which the policy does not restrict.

## Goals / Non-Goals

**Goals:**
- The same options and values as `colorScheme`, `locale`, `timezoneId` and `bypassCSP` of Browser's `New Context`, named like our other arguments.

**Non-Goals:**
- Turning `bypass_csp` on by default. It also applies to webviews and other frames, and a test would then miss CSP problems of the application or the extension under test.
- Locale and time zone of the main process. `TZ` in `env` and `--lang` in `args` already work for it.
- VS Code's display language. VS Code takes it from its `--locale` argument and a language pack, not from the page's locale.
- Fixing Browser's presenter mode, which falls back to the selector recorder when it cannot highlight an element. That is a matter of the Browser library.

## Decisions

### Arguments

- `New Electron Application` gets four arguments after `tracing`:
  - `color_scheme: ColorScheme | None = None`. `ColorScheme` is Browser's type, as for `New Context`. `None` and `null` both leave the color scheme to the application.
  - `locale: str | None = None` and `timezone_id: str | None = None`.
  - `bypass_csp: bool = False`.
- `Open VS Code` gets the same keyword-only arguments and passes them on.
- **Alternative:** an own type for the color scheme without `null`. Rejected: Browser's type brings the same values, conversion and documentation as `New Context`.

### Passing them to Node

- Python collects the given options under Playwright's names into one dictionary and passes it to `robotframeworkElectronLaunch` as `launchOptions`. Options that are not given are left out.
- `electron.js` starts `contextOptions` with the defaults `{ acceptDownloads: true, colorScheme: null }` and merges `launchOptions` into them. The options thus reach `_electron.launch` and `adoptContext` as the recording options do today.
- **Alternative:** one JavaScript parameter per option. Rejected: the function already has eleven parameters, and later options would then need changes on both sides.

### Default color scheme

- Without `color_scheme`, the application decides. Applications choose their theme themselves; Playwright's `light` is a default for web pages.
- This changes the look of dark applications in existing tests. In the pilot phase, there is no compatibility to keep. The screenshots of the documentation are regenerated, to see whether VS Code's look changes.

### Fixture and tests

- **Fixture:**
  - With `--dark`, the fixture app sets `nativeTheme.themeSource = 'dark'` before it opens its window.
  - With `--page=csp.html`, it loads `csp.html` instead of `index.html`. That page has the policy `default-src 'self'; script-src 'self'; require-trusted-types-for 'script'`.
- **Reading the effect:** the tests use `Evaluate JavaScript` with `matchMedia('(prefers-color-scheme: dark)').matches`, `navigator.language`, `Intl.DateTimeFormat().resolvedOptions().timeZone` and `(1234.5).toLocaleString()`.
- **Script element:** a script element with inline code is added through `Evaluate JavaScript`. With Trusted Types required, setting the element's `text` throws, so the test sees an error without `bypass_csp` and the script's effect with it. `Evaluate JavaScript` itself runs through the DevTools protocol and is not restricted by the policy.
- **Electron:** a suite `launch_options.robot` with one test per scenario. Unit tests check that only given options are passed, and that `electron.js` uses `colorScheme: null` unless one is given.
- **VS Code:** a suite `launch_options.robot` with one test per scenario.

### Documentation

- **Getting started for Electron:** a section on the launch options. It covers:
  - that the application decides the color scheme by default, and that `color_scheme` makes screenshots the same on every machine;
  - that `locale` and `timezone_id` apply to the windows, while `TZ` and `--lang` apply to the main process;
  - `bypass_csp`, and why it is off by default.
- **`Open VS Code`:** its keyword documentation says that VS Code's display language comes from `--locale` and a language pack.
- **Browser features guide:** a row for `Record Selector`, which needs `bypass_csp` in VS Code.

## Risks / Trade-offs

- [An application follows the system's theme, so a dark desktop and CI differ] → The documentation recommends `color_scheme` for tests that compare screenshots.
- [Users switch `bypass_csp` on everywhere] → The keyword documentation and the guide say that it also disables the policy of webviews, and recommend it only where a feature needs it.
- [A Playwright release drops one of the options for Electron] → The acceptance tests would show it at once.
