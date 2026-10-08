---
title: Test a VS Code extension
description: Open an isolated VS Code with your extension using robotframework-vscode and drive the workbench with Browser keywords.
sidebar:
  order: 2
---

`VSCode` is built on `Electron` and the [Browser library](https://robotframework-browser.org). It contains every Electron and Browser keyword, downloads VS Code, and starts isolated VS Code instances with the extension under test. The workbench window is an ordinary Browser page.

## Installation

Like `robotframework-electron`, the library needs a Browser hook that is not released yet. Until it is, install it from the repository's uv workspace, as described in the repository's `AGENTS.md`:

```sh
uv sync
```

Nothing from npm is needed. VS Code itself is downloaded on first use.

## First test

A test in an extension's repository, run from the extension's root folder (`${EXECDIR}`), with a workspace for the test in `tests/workspace`:

```robotframework
*** Settings ***
Library    VSCode

*** Test Cases ***
Extension Command Shows A Message
    Open VS Code    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
    Keyboard Key    press    F1
    Keyboard Input    type    Robot Test: Say Hello
    Wait For Elements State    .quick-input-list .monaco-list-row[aria-label*="Robot Test: Say Hello"]    visible
    Keyboard Key    press    Enter
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    Close VS Code
```

The command palette filters asynchronously, so the test waits for the command's row before pressing Enter.

## Opening VS Code

`Open VS Code` starts VS Code and returns once the workbench is ready. It returns the browser id, the context id and the page details of the workbench window, like `New Electron Application`.

- **Which VS Code:** `version` is `stable` (the default), `insiders` or a fixed version such as `1.141.0`. Alternatively, `executable` starts an installed VS Code or a [fork](../../guides/vscode-forks/) and downloads nothing.
- **Extensions:**
  - `extension_development_path` loads one or more extensions from source.
  - `extensions` installs Marketplace extensions or `.vsix` files into the instance before it starts.
  - `Install VS Code Extension` installs a Marketplace extension or a `.vsix` file into the running instance. VS Code picks it up without a restart.
- **Settings:** `settings` are written to the instance's user settings. The defaults switch off the welcome page, release notes, update checks, telemetry and workspace trust. They also switch off the screen reader mode, which VS Code otherwise turns on under Playwright, and hide the secondary side bar. Given settings override the defaults.
- **Isolation:** every instance gets its own user-data and extensions directories under the output directory. Neither the user's own VS Code nor other instances affect it. `VSCODE_*` variables and `ELECTRON_RUN_AS_NODE` are removed from its environment.
- **Closing:** `Close VS Code`, `Close Browser` and Browser's automatic closing end the instance.

## Next steps

- [CI and the Linux display](../../guides/ci-and-display/) for running without a desktop.
- [Downloads and cache](../../guides/downloads-and-cache/) for VS Code versions and offline runs.
- [Logs and troubleshooting](../../guides/logs/) for VS Code's logs and the instance directories.
