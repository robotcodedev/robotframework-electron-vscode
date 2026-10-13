# robotframework-electron

A [Robot Framework](https://robotframework.org) library for testing Electron applications. It is built on the [Browser library](https://robotframework-browser.org): `Electron` contains the Browser keywords that apply to applications, takes the same import arguments, and adds keywords to start, switch and close Electron applications. The windows of an application are ordinary Browser pages.

**Documentation:** https://robotcodedev.github.io/robotframework-electron-vscode/

## Installation

The library needs a small hook in the Browser library that is not released yet. Until it is, install it from its repository's uv workspace, which takes `robotframework-browser` from a local clone with the hook, as described in the repository's `AGENTS.md`:

```sh
uv sync
```

## Example

Import `Electron` instead of `Browser`. The library downloads nothing. For an app that runs on the plain Electron binary, the npm package `electron` provides the binary, `node_modules/electron/dist/electron` on Linux, and the app folder is passed as an argument:

```robotframework
*** Settings ***
Library    Electron

*** Variables ***
${ELECTRON_EXECUTABLE}    node_modules/electron/dist/electron

*** Test Cases ***
App From Source
    Start Electron Application    ${ELECTRON_EXECUTABLE}    args=${{ [$EXECDIR + "/app"] }}
```

The [documentation](https://robotcodedev.github.io/robotframework-electron-vscode/) covers starting and closing applications, providing Electron, running on CI and troubleshooting.
