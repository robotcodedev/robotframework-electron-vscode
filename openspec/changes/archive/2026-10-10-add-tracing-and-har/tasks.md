# Tasks

## 1. Browser hook

- [x] 1.1 Add the options `tracing` and `contextOptions` to `adoptContext` in the Browser clone, with Jest tests and an acceptance test that adopts a context with both, downloads a file and checks the trace. Propose them in MarketSquare/robotframework-browser#5318.

## 2. Electron

- [x] 2.1 Add `tracing` and `record_har` to `New Electron Application`. Resolve the trace path with Browser's helper, register the context for the keyword groups, resolve a relative HAR path against the output directory, and add unit tests for the HAR options.
- [x] 2.2 Build the context options in `electron.js` and pass them to `_electron.launch()` and as `contextOptions` to `adoptContext`.
- [x] 2.3 Add a local web server and a trace reader to the Electron test fixture, and the acceptance tests `tracing.robot`, `har.robot` and `download.robot`. Verify that the Electron acceptance tests pass.

## 3. VS Code

- [x] 3.1 Pass `tracing` and `record_har` from `Open VS Code` to `New Electron Application`, and add the acceptance test "Trace And HAR Of The Workbench". Verify that `uv run robotcode -r . analyze code` reports no errors or warnings.

## 4. Example and documentation

- [x] 4.1 Add `examples/vscode-extension/tests/tracing.robot` and mention it in the example's README. Verify that it passes with `-p xvfb`.
- [x] 4.2 Add the guide `docs/src/content/docs/guides/traces.mdx`, which includes the example suite, and list tracing, HAR recording and `Download` in the Browser features guide. Verify that `npm run build` in `docs/` succeeds.
