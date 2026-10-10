# Proposal

## Why

A Playwright trace shows step by step what a test did, with screenshots, snapshots and network requests, grouped by keyword. It is the most detailed way to find out why a test failed on CI. A HAR file records the network traffic. Browser offers both for the contexts it creates (`tracing` and `recordHar` of `New Context`), but an Electron application's context is created by Playwright's Electron support and handed over with `adoptContext`, so neither worked. `Download` failed on every adopted context with "Context acceptDownloads is false", because Browser did not know the options the context was created with.

This change was implemented before it was written down. The proposal records it after the fact.

## What Changes

- `New Electron Application` gets `tracing`, with the values of `tracing` of `New Context`, including `ROBOT_FRAMEWORK_BROWSER_TRACING`, and `record_har`, with the keys of `recordHar` of `New Context`.
- The trace is started and saved by Browser through the `adoptContext` option `tracing`. The library registers the context for Browser's keyword groups in the trace.
- `record_har` goes to Playwright's `_electron.launch()`, which writes the file when the context closes.
- The library passes the context options of the application, `acceptDownloads` and the recording options, to `adoptContext` as `contextOptions`, so that `Download` works.
- `Open VS Code` passes `tracing` and `record_har` on.
- The Browser hook gets the options `tracing` and `contextOptions`, proposed in MarketSquare/robotframework-browser#5318.
- The documentation site gets a guide on traces and HAR files with an example suite.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: traces, HAR files and downloads of an application.
- `vscode-launch`: `Open VS Code` records traces and HAR files the same way.
- `vscode-examples`: an example suite that records traces and a HAR file, shown in a guide.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, `packages/vscode/src/VSCode/__init__.py`.
- Acceptance tests `tracing.robot`, `har.robot` and `download.robot` with a local web server in the Electron test fixture, a VS Code test, and unit tests for the HAR options.
- `examples/vscode-extension/tests/tracing.robot`, the guide `docs/src/content/docs/guides/traces.mdx` and the Browser features guide.
- Depends on the options `tracing` and `contextOptions` of `adoptContext` in the Browser library.
