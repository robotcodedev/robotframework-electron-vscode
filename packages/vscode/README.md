# robotframework-vscode

A [Robot Framework](https://robotframework.org) library for end-to-end testing of VS Code extensions. It is built on `robotframework-electron` and the [Browser library](https://robotframework-browser.org): `VSCode` contains the Electron keywords and the Browser keywords that apply to applications, and starts isolated VS Code instances with the extension under test. The workbench window is an ordinary Browser page.

**Documentation:** https://robotcodedev.github.io/robotframework-electron-vscode/

## Installation

```sh
pip install robotframework-vscode
rfbrowser init --skip-browsers
```

The library brings `robotframework-electron` and the Browser library; `rfbrowser init` completes the installation of the Browser library.

The library starts a VS Code that you provide and downloads nothing: an installation, a portable copy, a fork, or a build that [`@vscode/test-electron`](https://www.npmjs.com/package/@vscode/test-electron) downloads. A variable such as `VSCODE_EXECUTABLE` in `robot.toml` names it.

## Example

A test in an extension's repository, run from the extension's root folder (`${EXECDIR}`), with a workspace for the test in `tests/workspace`:

```robotframework
*** Settings ***
Library    VSCode

*** Test Cases ***
Extension Command Shows A Message
    Start VS Code    ${VSCODE_EXECUTABLE}    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
    Keyboard Key    press    F1
    Keyboard Input    type    Robot Test: Say Hello
    Wait For Elements State    .quick-input-list .monaco-list-row[aria-label*="Robot Test: Say Hello"]    visible
    Keyboard Key    press    Enter
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    Close VS Code
```

The command palette filters asynchronously, so the test waits for the command's row before pressing Enter.

`Evaluate In Extension Host` runs JavaScript with VS Code's extension API in the extension host, for example to run a command by its id or to wait for a language server, see [the extension host](https://robotcodedev.github.io/robotframework-electron-vscode/vscode/extension-host/).

The [documentation](https://robotcodedev.github.io/robotframework-electron-vscode/) covers the options of `Start VS Code`, VS Code versions and profiles, VS Code forks, running on CI, and logs and troubleshooting.
