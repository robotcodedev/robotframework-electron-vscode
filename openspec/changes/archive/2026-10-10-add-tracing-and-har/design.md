# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements. Findings from 2026-10-10, with Playwright 1.63, Electron 44 and VS Code 1.141 under Xvfb:
- **Playwright:** `context.tracing.start()` and `stop()` and `context.tracing.startHar()` work on the context of an Electron application. `_electron.launch()` also takes `recordHar` like a context, and Playwright writes the HAR file when the context closes.
- **Browser:** Browser starts tracing only in `New Context` and `New Persistent Context`, from their `tracing` argument or `ROBOT_FRAMEWORK_BROWSER_TRACING`. An adopted context got no trace, even with the global setting.
- **Too late in `onClose`:** Browser calls `onClose` after it has closed the context, and `tracing.stop()` then fails with "Target page, context or browser has been closed". `stopHar()` still works then, but `recordHar` at launch is simpler.
- **`Download`:** It checks `acceptDownloads` in the context options that Browser keeps with each context. An adopted context had none, so `Download` failed, although Electron accepts downloads by default.
- **HAR content:** A HAR file holds the windows' traffic. Requests of the main process or VS Code's extension host are not in it.

## Goals / Non-Goals

**Goals:**
- Traces and HAR files of Electron applications and VS Code with the arguments and paths of `New Context`.
- Browser keywords that depend on context options, such as `Download`, work on applications.

**Non-Goals:**
- Tracing in Browser for every adopted context from its global setting. The creator decides, as with video.
- HAR recording through Browser. The launch option covers it.

## Decisions

- **`tracing` in Browser, the decision in the library.** `adoptContext` gets an option `tracing` with the trace path. Browser starts the trace and saves it before it closes the context, with the code it uses for `New Context`. The library resolves the path with Browser's `_resolve_trace_file`, which also handles `ROBOT_FRAMEWORK_BROWSER_TRACING`, and registers the context with `add_context_and_keyword_call_stack_to_trace`, so that the trace shows the keyword groups.
- **HAR as a launch option.** `record_har` goes to `_electron.launch()` like `record_video`. A relative path is resolved against the output directory, because a path relative to the Node process' working directory would be surprising.
- **The real context options.** `electron.js` builds the context options once, `acceptDownloads: true` (Electron's default) and the recording options if given, and passes the same object to `_electron.launch()` and as `contextOptions` to `adoptContext`. Process options such as `env` are not context options and stay out. Own data does not belong there either; nothing reads it back.

## Risks / Trade-offs

- [The library uses Browser's internal helpers `_resolve_trace_file` and `add_context_and_keyword_call_stack_to_trace`] → They are the same helpers `New Context` uses, and the acceptance tests fail if they change.
- [The options `tracing` and `contextOptions` are not yet in a Browser release] → They are part of MarketSquare/robotframework-browser#5318, and the clone carries them until then.
