---
title: Downloads and cache
description: How the libraries download Electron and VS Code, where they cache them, and how to use a local executable instead.
---

The libraries download Electron and VS Code themselves, so a test project needs nothing but Python and the libraries. Every download is checked against a published SHA-256 checksum and cached.

## VS Code

`Open VS Code` downloads VS Code when it is given a `version`:

- `stable`, the default, and `insiders` always ask the VS Code update service for the newest build.
- A fixed version such as `1.141.0` is downloaded once. When it is in the cache, it needs no network access.

To get a VS Code executable without starting it, for example in a CI setup step, use the helper library `VSCode.Helper`. It holds no browser state and can be imported on its own:

```robotframework
*** Settings ***
Library    OperatingSystem
Library    VSCode.Helper

*** Test Cases ***
VS Code Is Available
    ${code} =    Get VS Code Executable    1.141.0
    File Should Exist    ${code}
```

`Get VS Code Executable    version=stable    executable=${NONE}    cache_dir=${NONE}` returns the path of the executable. Builds are checked against the SHA-256 that the update service publishes.

## Electron

`Get Electron Executable` from `Electron.Helper` downloads an Electron release from GitHub, checks it against the release's `SHASUMS256.txt`, and returns the path of the Electron binary:

```robotframework
*** Settings ***
Library    OperatingSystem
Library    Electron.Helper

*** Test Cases ***
Electron Is Available
    ${electron} =    Get Electron Executable    44.7.0
    File Should Exist    ${electron}
```

## Where the cache is

Both libraries cache in the user's cache directory (`~/.cache` on Linux, `~/Library/Caches` on macOS, `%LOCALAPPDATA%` on Windows):

- VS Code in `robotframework-vscode/vscode`,
- Electron in `robotframework-electron/electron`.

All keywords that download take a `cache_dir` that replaces this location.

## A local executable instead of a download

If `executable` is given, `Open VS Code`, `Get VS Code Executable` and `Get Electron Executable` use it and download nothing. With variables that default to `${NONE}`, a suite downloads by default and can switch to a local executable without changing the tests:

```robotframework
*** Settings ***
Library    VSCode

*** Variables ***
${VSCODE_VERSION}       1.141.0
${VSCODE_EXECUTABLE}    ${NONE}
${VSCODE_CACHE}         ${NONE}

*** Test Cases ***
Workbench Opens
    Open VS Code    ${EXECDIR}/tests/workspace
    ...    version=${VSCODE_VERSION}
    ...    executable=${VSCODE_EXECUTABLE}
    ...    cache_dir=${VSCODE_CACHE}
    ...    extension_development_path=${EXECDIR}
    Get Title    contains    Visual Studio Code
    Close VS Code
```

Set the variable on the command line, for example `--variable VSCODE_EXECUTABLE:/usr/share/code/code`, or, with RobotCode, in a personal `.robot.toml` that is not checked in:

```toml
[variables]
VSCODE_EXECUTABLE = "/usr/share/code/code"
```
