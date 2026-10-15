---
title: Logs and troubleshooting
description: Where to find the logs of a run, and what to check when an application does not start.
sidebar:
  order: 2
---

## Logs of a run

Besides Robot Framework's own `log.html`, the output directory holds `playwright-log.txt`. It is the log of the Browser library's Node.js side and shows its calls to Playwright, with their errors. VS Code keeps logs of its own, see [Instances, logs and troubleshooting](../../vscode/instances/).

## Troubleshooting

**The Electron binary behaves like Node.js.** Runs started from VS Code, for example from its terminal or test explorer, inherit `ELECTRON_RUN_AS_NODE=1`, which makes every Electron binary run as plain Node.js. `Start Electron Application` and `Start VS Code` remove that variable. If you pass `env` to `Start Electron Application` yourself, leave it out there.

**An application cannot be started.** Playwright attaches to an Electron application through the Node.js inspector. Applications built with the Electron fuse `EnableNodeCliInspectArguments` switched off cannot be started.

**Windows show up on the desktop although the tests run under `xvfb-run`.** On a Wayland desktop, see [CI and the Linux display](../ci-and-display/).

**Browser keywords are ambiguous.** `Electron` and `VSCode` contain most Browser keywords. A suite that imports `Browser` beside them, or both of them, needs full keyword names such as `Browser.New Page` for the keywords they share, or the usual Robot Framework means such as `Set Library Search Order`.
