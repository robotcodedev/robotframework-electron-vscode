# robotframework-electron

A [Robot Framework](https://robotframework.org) library for testing Electron applications. It is built on the [Browser library](https://robotframework-browser.org): `Electron` contains every Browser keyword, takes the same import arguments, and adds keywords to start and close Electron applications. The windows of an application are ordinary Browser pages.

## Installation

The library needs a small hook in the Browser library that is not released yet. Until it is, install it from this repository's uv workspace. That workspace takes `robotframework-browser` from a local clone with the hook, as described in the repository's `AGENTS.md`.

```sh
uv sync
```

## Usage

Import `Electron` instead of `Browser`:

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

For an app that runs on the plain Electron binary, pass the app folder as an argument. `Get Electron Executable` from the `Electron.Helper` library provides that binary:

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
    New Electron Application    ${electron}    args=${{ ["path/to/app"] }}
```

`Get Electron Executable` downloads the given release from GitHub on first use, checks its SHA-256 checksum and caches it in the user's cache directory, or in `cache_dir` if given. If `executable` is set, for example with `--variable ELECTRON_EXECUTABLE:/path/to/electron`, it returns that path and downloads nothing.

- `New Electron Application` returns the browser id, the context id and the details of the first window's page, like `New Persistent Context`.
- Windows that the app opens later can be selected with `Switch Page    NEW`.
- `Close Electron Application`, `Close Browser`, `Close Context` and Browser's automatic closing all end the application.

## Notes

- **Linux without a desktop** needs a display server, for example `xvfb-run -a robot ...`.
- **Runs started from VS Code** inherit `ELECTRON_RUN_AS_NODE=1`, which makes every Electron binary run as plain Node.js. `New Electron Application` removes that variable unless you pass `env` yourself.
- **Apps with the Node inspector disabled** (Electron fuse `EnableNodeCliInspectArguments`) cannot be started, because Playwright needs the inspector to attach to the main process.
- **Importing both `Browser` and `Electron`** makes every Browser keyword ambiguous. Import only `Electron`, or use the usual Robot Framework means such as `Set Library Search Order` or full keyword names.

## Development

```sh
uv run pytest packages/electron/tests
xvfb-run -a uv run robot --outputdir results packages/electron/atest
```

The acceptance tests get Electron through `Electron.Helper` with the repository's `.cache/electron/` as cache, and use the fixture app in `atest/fixtures/app/`. The Electron version is the variable `${ELECTRON_VERSION}` in `atest/resources/fixture.resource`. To run against another version, override it, for example `--variable ELECTRON_VERSION:42.11.12`. To use a local Electron without downloading, pass `--variable ELECTRON_EXECUTABLE:/path/to/electron`. The test `Application And Web Browser` also needs Chromium for Playwright in the Browser clone: run `PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium` there.
