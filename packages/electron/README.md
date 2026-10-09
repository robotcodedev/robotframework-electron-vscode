# robotframework-electron

A [Robot Framework](https://robotframework.org) library for testing Electron applications. It is built on the [Browser library](https://robotframework-browser.org): `Electron` contains every Browser keyword, takes the same import arguments, and adds keywords to start and close Electron applications. The windows of an application are ordinary Browser pages.

**Documentation:** https://robotcodedev.github.io/robotframework-electron-vscode/

## Installation

The library needs a small hook in the Browser library that is not released yet. Until it is, install it from its repository's uv workspace, which takes `robotframework-browser` from a local clone with the hook, as described in the repository's `AGENTS.md`:

```sh
uv sync
```

## Example

Import `Electron` instead of `Browser`. For an app that runs on the plain Electron binary, `Get Electron Executable` from `Electron.Helper` downloads Electron, and the app folder is passed as an argument:

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

The [documentation](https://robotcodedev.github.io/robotframework-electron-vscode/) covers starting and closing applications, downloads, running on CI and troubleshooting.
