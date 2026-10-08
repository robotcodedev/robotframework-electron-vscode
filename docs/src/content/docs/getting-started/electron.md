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

## Next steps

- [CI and the Linux display](../../guides/ci-and-display/) for running without a desktop.
- [Logs and troubleshooting](../../guides/logs/) if an app does not start.
