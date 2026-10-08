---
title: Logs and troubleshooting
description: Where to find the logs of a run and of VS Code, and what to check when an application does not start.
---

## Logs of a run

Besides Robot Framework's own `log.html`, the output directory holds `playwright-log.txt`. It is the log of the Browser library's Node.js side and shows its calls to Playwright, with their errors.

## VS Code instance directories

Every instance that `Open VS Code` starts gets its own folder `vscode/<n>` in the output directory, numbered from 1, with its user-data and extensions directories. The folders stay after the run, so VS Code's own logs can be read afterwards:

- `vscode/<n>/user-data/logs/<timestamp>/main.log` for the main process,
- `vscode/<n>/user-data/logs/<timestamp>/window1/` for the window, with the extension host's log in `exthost/exthost.log`.

When a run starts, the library removes the `vscode` folder that earlier runs left in the same output directory, the way Browser cleans its own output folders. Two runs that use the same output directory at the same time would remove each other's folders, so give parallel runs their own output directories. pabot does that already.

## Troubleshooting

**The Electron binary behaves like Node.js.** Runs started from VS Code, for example from its terminal or test explorer, inherit `ELECTRON_RUN_AS_NODE=1`, which makes every Electron binary run as plain Node.js. `New Electron Application` and `Open VS Code` remove that variable. If you pass `env` to `New Electron Application` yourself, leave it out there.

**An application cannot be started.** Playwright attaches to an Electron application through the Node.js inspector. Applications built with the Electron fuse `EnableNodeCliInspectArguments` switched off cannot be started.

**Windows show up on the desktop although the tests run under `xvfb-run`.** On a Wayland desktop, see [CI and the Linux display](../ci-and-display/).

**The command palette runs the wrong command.** The palette filters asynchronously. Wait for the command's row before pressing Enter, as in [the first VS Code test](../../getting-started/vscode/).

**Every Browser keyword is ambiguous.** `Electron` and `VSCode` contain all Browser keywords. Import only one of the libraries, or use the usual Robot Framework means such as `Set Library Search Order` or full keyword names.
