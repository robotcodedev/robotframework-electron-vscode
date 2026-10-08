# robotframework-vscode

A [Robot Framework](https://robotframework.org) library for end-to-end testing of VS Code extensions. It is built on [robotframework-electron](../electron/README.md) and the [Browser library](https://robotframework-browser.org): `VSCode` contains every Electron and Browser keyword, downloads VS Code, and starts isolated VS Code instances with the extension under test. The workbench window is an ordinary Browser page.

## Installation

Like `robotframework-electron`, the library needs a Browser hook that is not released yet. Until it is, install it from this repository's uv workspace, as described in the repository's `AGENTS.md`:

```sh
uv sync
```

Nothing from npm is needed. VS Code itself is downloaded on first use.

## Quick start

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

- **Which VS Code:** `version` is `stable` (the default), `insiders` or a fixed version such as `1.141.0`. Alternatively, `executable` starts an installed VS Code and downloads nothing.
- **Extensions:**
  - `extension_development_path` loads one or more extensions from source.
  - `extensions` installs Marketplace extensions or `.vsix` files into the instance before it starts.
- **Settings:** `settings` are written to the instance's user settings. The defaults switch off the welcome page, release notes, update checks, telemetry and workspace trust. They also switch off the screen reader mode, which VS Code otherwise turns on under Playwright, and hide the secondary side bar. Given settings override the defaults.
- **Isolation:** every instance gets its own user-data and extensions directories in `vscode/<n>` under the output directory. Neither the user's own VS Code nor other instances affect it. `VSCODE_*` variables and `ELECTRON_RUN_AS_NODE` are removed from its environment. The directories stay after the run, so VS Code's logs are in `vscode/<n>/user-data/logs`.
- **Cleanup:** when a run starts, the library removes the `vscode` folder that earlier runs left in the same output directory, the way Browser cleans its own output folders. The instances of the current run are kept and numbered from 1. Two runs that use the same output directory at the same time would remove each other's folders, so give parallel runs their own output directories; pabot does that already.
- **Closing:** `Close VS Code`, `Close Browser` and Browser's automatic closing end the instance.

## Downloads and cache

`Open VS Code` downloads VS Code when it is given a `version`. To get a VS Code executable without starting it, for example in a CI setup step, use the helper library `VSCode.Helper`. It holds no browser state and can be imported on its own:

```robotframework
*** Settings ***
Library    OperatingSystem
Library    VSCode.Helper

*** Test Cases ***
VS Code Is Available
    ${code} =    Get VS Code Executable    1.141.0
    File Should Exist    ${code}
```

`Get VS Code Executable    version=stable    executable=${NONE}    cache_dir=${NONE}` returns the path of the executable. If `executable` is given, it returns it unchanged and downloads nothing, so a suite can switch to a local VS Code through a variable.

Every download is checked against the SHA-256 that the VS Code update service publishes. Builds are cached in `robotframework-vscode/vscode` in the user's cache directory (`~/.cache` on Linux, `~/Library/Caches` on macOS, `%LOCALAPPDATA%` on Windows), or in `cache_dir` if given. A fixed version that is already cached needs no network access. `stable` and `insiders` always ask the update service for the newest build.

## VS Code forks

Forks of VS Code, such as VSCodium, run with `executable` set to the fork's executable:

```robotframework
Open VS Code    ${EXECDIR}/tests/workspace    executable=/opt/vscodium/codium    extension_development_path=${EXECDIR}
```

- `version` downloads only Microsoft's VS Code builds. For a fork, always give `executable`.
- Extensions in `extensions` are installed with the fork's own command-line script, which the library finds through `applicationName` in the fork's `product.json`. They come from the fork's own extension gallery. VSCodium, for example, uses Open VSX, so extensions that exist only in Microsoft's Marketplace are not available there.
- VSCodium 1.135 passes this library's own VS Code tests, except that it writes no log files to `user-data/logs`.
- Cursor has not been tried yet. It ships as an AppImage, which has to be extracted first. If Cursor's Electron build switches off the Node.js inspector (Electron fuse `EnableNodeCliInspectArguments`), Playwright cannot attach to it.

To run this repository's VS Code tests against a fork, point `VSCODE_EXECUTABLE` at it and leave out the tests that check VS Code's own behaviour:

```sh
uv run robotcode -r . robot -v VSCODE_EXECUTABLE:/opt/vscodium/codium -e vscode-only -bl "Electron & VSCode.VSCode"
```

## Linux display

VS Code needs a display.
- **Without a desktop**, for example on CI, run the tests under `xvfb-run -a`.
- **On a Wayland desktop**, VS Code opens its windows on the desktop, even under `xvfb-run`, because it follows `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE`. To run hidden in Xvfb, use:

```sh
env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 xvfb-run -a uv run robotcode -r . robot
```

## Development

```sh
# from the repository root
uv run pytest
uv run robotcode -r . robot                          # acceptance tests, configured in robot.toml
uv run robotcode -r . -p vscode-insiders robot       # against the newest VS Code Insiders
```

The acceptance tests are in `atest/`, with a plain JavaScript test extension in `atest/fixtures/extension/` and a test workspace in `atest/fixtures/workspace/`. The VS Code version is the variable `${VSCODE_VERSION}` in `atest/resources/vscode.resource`, and builds are cached in the repository's `.cache/vscode/`. To use an installed VS Code, set `VSCODE_EXECUTABLE` in a personal, gitignored `.robot.toml`:

```toml
[variables]
VSCODE_EXECUTABLE = "/path/to/code"
```
