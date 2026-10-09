# robotframework-vscode

A [Robot Framework](https://robotframework.org) library for end-to-end testing of VS Code extensions. It is built on `robotframework-electron` and the [Browser library](https://robotframework-browser.org): `VSCode` contains every Electron and Browser keyword, downloads VS Code, and starts isolated VS Code instances with the extension under test. The workbench window is an ordinary Browser page.

**Documentation:** https://robotcodedev.github.io/robotframework-electron-vscode/

## Installation

Like `robotframework-electron`, the library needs a Browser hook that is not released yet. Until it is, install it from its repository's uv workspace, as described in the repository's `AGENTS.md`:

```sh
uv sync
```

Nothing from npm is needed. VS Code itself is downloaded on first use.

## Example

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

The [documentation](https://robotcodedev.github.io/robotframework-electron-vscode/) covers the options of `Open VS Code`, downloads and cache, VS Code forks, running on CI, and logs and troubleshooting.
