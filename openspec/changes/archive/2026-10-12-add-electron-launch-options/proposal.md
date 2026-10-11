# Proposal

## Why

`_electron.launch` takes a few context options that decide how an application looks and behaves under test, and `New Electron Application` passes none of them:

- **Color scheme:** without `colorScheme`, Playwright emulates `prefers-color-scheme: light`. A dark application looks light under test, even when it sets `nativeTheme.themeSource = 'dark'`.
- **Locale and time zone:** language, number and date formats follow the machine, so local runs and CI differ. `--lang` changes only `navigator.language`, not the formatting.
- **Content Security Policy:** VS Code's workbench requires Trusted Types for scripts. Browser features that add a script to the page fail there, for example `Record Selector`: "This document requires 'TrustedScript' assignment". A test on 2026-10-09 showed that `bypassCSP` helps.

This change replaces the open change `add-electron-bypass-csp` and takes over its content.

## What Changes

- **`New Electron Application`** gets four arguments and passes them to `_electron.launch`:
  - `color_scheme`. By default the application decides; `light` or `dark` emulate the color scheme.
  - `locale`, for example `de-DE`.
  - `timezone_id`, for example `Europe/Berlin`.
  - `bypass_csp`, default `False`.
- **The default color scheme changes:** without `color_scheme`, the application now decides instead of Playwright's emulated `light`.
- **`Open VS Code`** passes the four arguments on.
- **Fixture app:** it can switch its theme to dark (`--dark`) and open a page with a strict Content Security Policy (`--page=csp.html`).
- **Documentation:** the getting-started page for Electron explains the options, and the Browser features guide names `bypass_csp` for `Record Selector` in VS Code.
- **Not part of this change:** the other options of `_electron.launch`, such as `ignoreHTTPSErrors`, `extraHTTPHeaders` and `httpCredentials`, until a test needs them. `offline` and `geolocation` exist as runtime keywords.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: color scheme, locale and time zone, and bypassing the Content Security Policy.
- `vscode-launch`: `Open VS Code` passes these options on.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, `packages/vscode/src/VSCode/__init__.py`.
- The Electron fixture app, unit tests and acceptance tests in both packages.
- `docs/`: the getting-started page for Electron and the Browser features guide.
- `openspec/changes/add-electron-bypass-csp/` was removed when this change was created.
