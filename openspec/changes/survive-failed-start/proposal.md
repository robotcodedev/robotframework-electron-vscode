# Proposal

## Why

A failed start of an application can end Browser's whole Node process. If the application ends or the time runs out before Electron's first line of output, Playwright leaves promises without a handler, and they end the process. The test then sees only `Stream removed (Socket closed)`, an application that was already open is gone, and every later Browser keyword fails.

This breaks the promise of "Failed start", and it happens in realistic cases: on a CI runner that lacks a system library, and with every application built with the Electron fuse `EnableNodeCliInspectArguments` switched off. The cause is in Playwright, but it is unclear when a fix would reach Browser, and the libraries can prevent the damage themselves.

## What Changes

- **Failed start:** `Start Electron Application` and `Start VS Code` fail with Playwright's own error, whose call log shows the application's output and exit code. Applications and browsers that are already open keep working, and the next start works.
- **Handler around the launch:** `electron.js` ignores unhandled rejections while Playwright's launch runs, and only then. The launch itself still rejects with the error.
- **Troubleshooting guide:** it names the two errors of a failed start, `Process failed to launch!` and a timeout, and what they mean.

Not part of this change:

- A report to Playwright, which has the cause. If Playwright fixes it, the handler goes away.
- A handler in Browser's Node process, which would protect it from every such rejection. That would be an addition to Browser.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: "Failed start" also promises that what is already open keeps working and that the next start works, with new scenarios for an application that ends during the start and for time that runs out before the application answers.
- `vscode-launch`: "Start VS Code" gets a scenario for a VS Code that does not start.

## Impact

- **Code:** `packages/electron/src/Electron/electron.js`. Keywords and their arguments do not change.
- **Tests:** `packages/electron/tests/test_electron_js.py`, `packages/electron/atest/failed_start.robot` and `packages/vscode/atest/start_vs_code.robot`.
- **Documentation:** `docs/src/content/docs/running/logs.md`.
- **Order of the changes:** `use-browser-release` changes "Failed start" as well, and the delta here builds on its text, so that change is archived first.
