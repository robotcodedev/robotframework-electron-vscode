# Design

## Context

See proposal.md for why this matters.

[Playwright's `Electron.launch`](https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/electron/electron.ts#L259-L275) starts four waits for lines of Electron's output at once, because a line could otherwise pass unseen. Until the first line, `Debugger listening`, has come, only the wait for that line has a handler. If the process ends or the time runs out before it, all four reject, and the other three become unhandled rejections. Browser's Node server has no handler for those, so Node ends the process, as it does by default. Playwright's `main` has the same code as 1.64.1.

Measured on 2026-11-02 with Browser 21.0.0 and Playwright 1.64.1. The library with the handler was a copy of `Electron` in the scratchpad. "Lost" means: the keyword fails with `Stream removed (Socket closed)`, the application that was open before is gone, and the next start fails.

| Start | Without the handler | With the handler |
|---|---|---|
| `/bin/false` | lost | `electron.launch: Process failed to launch!` |
| Real Electron that lacks a system library, made with `patchelf --add-needed` | lost | the same, and the call log shows `error while loading shared libraries` and `exitCode=127` |
| Real Electron with the fuse `EnableNodeCliInspectArguments` off, made with `@electron/fuses` | lost, after the library timeout | `electron.launch: Timeout 10000ms exceeded.`, and the call log has no line `Debugger listening` |
| Real Electron with `timeout=50ms` | lost | `electron.launch: Timeout 50ms exceeded.` |
| `Start VS Code` with `/bin/false` | lost | `electron.launch: Process failed to launch!` |
| `/bin/false` with BrowserBatteries, no Node.js | lost | `electron.launch: Process failed to launch!` |

With the handler, the application that was open before keeps working and the next start works in all of these. In none of them, with or without the handler, was a process of the failed application left over.

Without Browser and without the libraries, a script with only Playwright and a `try/catch` around `_electron.launch` shows the same: Node ends with exit code 1, and the `catch` is never reached. With a handler in the script, it reports three rejections, and then the right error arrives in the `catch`. Without a display, the start fails cleanly even without a handler, because `Debugger listening` comes first.

## Goals / Non-Goals

**Goals:**

- A failed start costs a test only that start.
- The workaround stays in one place, so that it can go away when Playwright is fixed.

**Non-Goals:**

- A message of our own for a failed start.
- Protecting Browser's Node process from unhandled rejections outside the start.
- Starting applications that have the fuse switched off. They still cannot be started; they now fail with the right error.

## Decisions

### A handler only while the launch runs

`electron.js` calls `process.on('unhandledRejection', ...)` right before `playwright._electron.launch(...)` and removes the listener in a `finally`, when the launch has settled. The listener does nothing, because the launch itself rejects with the same error.

This is enough because of the order of events. The three promises reject in the same step as the wait that Playwright handles, so Node reports them as soon as the queue of microtasks is empty. The rejection of the launch arrives later, because Playwright's client gets it from its server through a message, even in the same process. Measured with timeouts from 1 to 1000 ms around the first line, which takes about 90 ms on the test machine, and a listener removed right after the launch settled:

| | Started | Clean timeout | Node process ended |
|---|---|---|---|
| Without a listener, 69 runs | 12 | 27 | 30, all at 90 ms or less |
| With the listener, 115 runs | 21 | 94 | 0 |

The listener patches nothing in Playwright or Browser, it only listens on Node's own `process`. Each start has its own listener, so starts that overlap do not remove each other's.

The alternatives:

- **A fix in Playwright:** three handlers there are the right fix, but they are out of our hands and would reach us only through a Browser release. When Browser ships a Playwright with the fix, the listener goes away.
- **A handler in Browser's Node process:** it would also protect Browser's other users and every extension. It is an addition to Browser and would raise our lower bound, so it does not replace this change.
- **`NODE_OPTIONS=--unhandled-rejections=warn`:** it applies to the whole process for the whole run, has to be set before Browser starts its Node process, and is inherited by the started applications.
- **A check before the start, such as running the executable with `--version`:** it finds neither the fuse nor the case of the time running out, and it starts the executable twice.

### Playwright's error stays as it is

The error already carries what a user needs, because the call log shows the output and the exit code of the process (see Context). `Start Electron Application` passes it on unchanged. A message of our own could not know more than the call log, and the guide explains the two errors.

### Tests

- **Unit test in `test_electron_js.py`:** the fake `launch` leaves a rejected promise behind, as Playwright does, and then rejects. Without the listener, the harness's Node process ends, and `check=True` fails the test. The test also checks that no listener is left, after a successful launch as well.
- **Acceptance tests in `failed_start.robot`:** an application is open, the start fails, the application still answers, and a new start works.
  - **A program that ends at once:** `${{ sys.executable }}`. Python refuses Playwright's `--no-sandbox`, prints its usage and ends with exit code 2, measured with Python 3.11, 3.13 and 3.15. This needs no fixture and no platform-specific program. The first line differs between Python versions, so the test looks for `usage:`.
  - **Time that runs out before the application answers:** the fixture application with `timeout=50ms`.
- **Acceptance test in `start_vs_code.robot`:** the same with `Start VS Code` and `${{ sys.executable }}`.

The real Electron without a system library and the one with the fuse switched off are not part of the tests, because they need a modified binary. They go through the same code path as the two cases above.

### The guide

The section "Troubleshooting" of `running/logs.md` gets a new entry before "An application cannot be started", and that entry gets a second sentence:

```md
**`Process failed to launch!`.** The executable ended before the application answered. The call log in the error shows its output and exit code, for example `error while loading shared libraries` on a system without the packages that Electron needs, see [CI and the Linux display](../ci-and-display/#vs-code-and-electron-on-ci).

**An application cannot be started.** Playwright attaches to an Electron application through the Node.js inspector. Applications built with the Electron fuse `EnableNodeCliInspectArguments` switched off cannot be started. `Start Electron Application` then fails with a timeout, and the call log in the error has no line `Debugger listening`.
```

## Risks / Trade-offs

- [A rejection that has nothing to do with the start goes unnoticed while a start runs] → Accepted. Without the listener it would end the process, and the listener is only there during the launch.
- [A later Playwright reports the rejections only after the launch has rejected] → The process then dies as it does today. The acceptance tests fail with `Stream removed` when the lock file moves to that Playwright, before users get it from us.
- [On a much faster machine, Electron's first line comes within 50 ms] → That test then passes without reaching the case. The test with `${{ sys.executable }}` does not depend on timing.
