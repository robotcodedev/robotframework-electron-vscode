---
title: Test an Electron app
description: Start an Electron application with robotframework-electron and test its windows with Browser keywords.
sidebar:
  order: 1
---

`Electron` is the [Browser library](https://robotframework-browser.org) plus keywords to start and close Electron applications. It contains every Browser keyword and takes the same import arguments. The windows of an application are ordinary Browser pages.

## Installation

The library needs a small hook in the Browser library that is not released yet. Until it is, install it from the repository's uv workspace. That workspace takes `robotframework-browser` from a local clone with the hook, as described in the repository's `AGENTS.md`.

```sh
uv sync
```

## First test

Import `Electron` instead of `Browser`, start the application, and use Browser keywords on its window:

```robotframework
*** Settings ***
Library    Electron

*** Test Cases ***
Greeting Is Shown
    New Electron Application    /opt/my-app/my-app
    Click    text=Say hello
    Get Text    id=greeting    ==    Hello!
    Close Electron Application
```

## An app from source

An app that runs on the plain Electron binary gets its app folder as an argument. `Get Electron Executable` from the `Electron.Helper` library provides the binary:

```robotframework
*** Settings ***
Library    Electron
Library    Electron.Helper

*** Variables ***
${ELECTRON_VERSION}       44.7.0
${ELECTRON_EXECUTABLE}    ${NONE}

*** Test Cases ***
App From Source
    ${electron} =    Get Electron Executable    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}
    New Electron Application    ${electron}    args=${{ [$EXECDIR + "/app"] }}
```

`Get Electron Executable` downloads the given Electron release on first use and caches it. If `executable` is set, for example with `--variable ELECTRON_EXECUTABLE:/path/to/electron`, it returns that path and downloads nothing. See [Downloads and cache](../../guides/downloads-and-cache/).

## Windows and closing

- `New Electron Application` returns the browser id, the context id and the details of the first window's page, like `New Persistent Context`.
- Windows that the app opens later can be selected with `Switch Page    NEW`.
- `Close Electron Application`, `Close Browser`, `Close Context` and Browser's automatic closing all end the application.

## The main process

Browser keywords reach the windows, but not the application's main process. `Evaluate In Main Process` runs a JavaScript function there. The function gets the `electron` module, the keyword's `arg`, and the `BrowserWindow` that shows the active page.

Native dialogs, such as file dialogs and message boxes, are outside the page, so no Browser keyword can click them. Replace them before the application opens them:

```robotframework
Evaluate In Main Process    ({ dialog }, path) => {
...        dialog.showOpenDialog = async () => ({ canceled: false, filePaths: [path] });
...    }
...    arg=${EXECDIR}/data/report.csv
Click    text=Open report
```

`showSaveDialog` and `showMessageBox` are replaced the same way. The replacement takes effect when the application calls the dialog through the module, as in `dialog.showOpenDialog(…)`, and lasts until the application ends.

The function can also read the application's state or size the window of the active page:

```robotframework
${version} =    Evaluate In Main Process    ({ app }) => app.getVersion()
Evaluate In Main Process    (electron, size, window) => window.setBounds(size)    arg=${{ {"width": 1280, "height": 720} }}
```

## Launch options

`New Electron Application` takes some of the options that `New Context` has for a web browser. They apply from the start, so another value means starting the application again.

```robotframework
New Electron Application    /opt/my-app/my-app    color_scheme=dark    locale=pt-BR    timezone_id=Asia/Tokyo
```

- **`color_scheme`:** by default, the application decides its color scheme, as it does outside of tests. With `light` or `dark`, its windows report that color scheme for `prefers-color-scheme`. Set it for tests that compare screenshots, so that the application looks the same on every machine.
- **`locale` and `timezone_id`:** they set the language that the windows report, their number and date formats, and their time zone. By default, they follow the system, so a test run on your machine can differ from CI. They do not reach the main process: there, `--lang` in `args` sets the locale and `TZ` in `env` the time zone.
- **`bypass_csp`:** the windows ignore their Content Security Policy, including Trusted Types. Browser features that add a script to the page need it in applications with a strict policy, for example `Record Selector` in VS Code. It is off by default, because it also switches off the policy of webviews and frames, and a test would then miss policy problems of the application.

## Next steps

- [Browser keywords in applications](../../guides/browser-keywords/) for what works on an application's windows and what does not.
- [CI and the Linux display](../../guides/ci-and-display/) for running without a desktop.
- [Logs and troubleshooting](../../guides/logs/) if an app does not start.
