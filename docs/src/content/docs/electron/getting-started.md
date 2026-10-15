---
title: Test an Electron app
description: Start an Electron application with robotframework-electron and test its windows with Browser keywords.
sidebar:
  label: Getting started
  order: 1
---

`Electron` is the [Browser library](https://robotframework-browser.org) plus keywords to start, switch and close Electron applications. It contains the Browser keywords that apply to applications and takes the same import arguments. The windows of an application are ordinary Browser pages.

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
    Start Electron Application    /opt/my-app/my-app
    Click    text=Say hello
    Get Text    id=greeting    ==    Hello!
    Close Electron Application
```

## An app from source

An app that runs on the plain Electron binary gets its app folder as an argument. The npm package `electron` provides the binary in the version that the app needs, and in Node, `require('electron')` returns its executable:

```sh
npm install --save-dev electron@44.7.0
node -p "require('electron')"
```

The package needs Node.js 22.12 or later and downloads the binary on first use, into the user's cache directory, or into the folder that the environment variable `electron_config_cache` names. The library downloads nothing itself. A variable in `robot.toml` holds the executable's path, on Linux `node_modules/electron/dist/electron`:

```toml
[variables]
ELECTRON_EXECUTABLE = "node_modules/electron/dist/electron"
```

```robotframework
*** Settings ***
Library    Electron

*** Test Cases ***
App From Source
    Start Electron Application    ${ELECTRON_EXECUTABLE}    args=${{ [$EXECDIR + "/app"] }}
```

## Windows and closing

- `Start Electron Application` returns the application id and the details of the first window's page: `${app}    ${page} =    Start Electron Application    …`.
- Windows that the app opens later can be selected with `Switch Page    NEW`.
- `Close Electron Application` and Browser's automatic closing end the application.
- Several applications can be open at once. `Switch Electron Application` switches between them.
- The library hides Browser's keywords for browsers and contexts, such as `New Page` and `Close Browser`. [Browser keywords in applications](../browser-keywords/#compared-with-the-browser-library) compares the two libraries.

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

`Start Electron Application` takes some of the options that the Browser library's `New Context` has for a web browser. They apply from the start, so another value means starting the application again.

```robotframework
Start Electron Application    /opt/my-app/my-app    color_scheme=dark    locale=pt-BR    timezone_id=Asia/Tokyo
```

- **`color_scheme`:** by default, the application decides its color scheme, as it does outside of tests. With `light` or `dark`, its windows report that color scheme for `prefers-color-scheme`. Set it for tests that compare screenshots, so that the application looks the same on every machine.
- **`locale` and `timezone_id`:** they set the language that the windows report, their number and date formats, and their time zone. By default, they follow the system, so a test run on your machine can differ from CI. They do not reach the main process: there, `--lang` in `args` sets the locale and `TZ` in `env` the time zone.
- **`bypass_csp`:** the windows ignore their Content Security Policy, including Trusted Types. Browser features that add a script to the page need it in applications with a strict policy, for example `Record Selector` in VS Code. It is off by default, because it also switches off the policy of webviews and frames, and a test would then miss policy problems of the application.

## Next steps

- [Browser keywords in applications](../browser-keywords/) for what works on an application's windows and what does not.
- [Traces and HAR files](../traces/) and [Videos and slow motion](../videos/) for recording what a test did.
- [CI and the Linux display](../../running/ci-and-display/) for running without a desktop.
- [Logs and troubleshooting](../../running/logs/) if an app does not start.
