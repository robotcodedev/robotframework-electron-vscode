# Proposal

## Why

Electron applications often protect their pages with a Content Security Policy. VS Code's workbench allows scripts only from its own files and requires Trusted Types for scripts (`script-src 'self' 'unsafe-eval' blob:`, `require-trusted-types-for 'script'`). Browser features that put a script into the page therefore fail there, for example `Record Selector`, which adds its recorder with Playwright's `addScriptTag`: "Failed to set the 'text' property on 'HTMLScriptElement': This document requires 'TrustedScript' assignment". Browser's `New Context` has the option `bypassCSP` for this. `_electron.launch` accepts the same option, and a test on 2026-10-09 showed that with it, inline scripts and Browser's selector recorder can be added to VS Code. `New Electron Application` does not pass the option yet.

## What Changes

- `New Electron Application` gets the argument `bypass_csp`, default `False`, and passes it to `_electron.launch` as `bypassCSP`. The page's Content Security Policy, including its Trusted Types, is then not enforced.
- `Open VS Code` passes `bypass_csp` on.
- The Electron fixture app can open a page with a strict Content Security Policy, so that the acceptance tests see the difference.
- The documentation explains when to use the option and why it is off by default: it also switches off the CSP of webviews, so that CSP problems of an extension would go unnoticed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: bypassing the page's Content Security Policy.
- `vscode-launch`: `Open VS Code` passes the option on.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, `packages/vscode/src/VSCode/__init__.py`.
- The Electron fixture app and acceptance tests in both packages.
- `docs/`: the Browser features guide and the getting-started page for Electron.
