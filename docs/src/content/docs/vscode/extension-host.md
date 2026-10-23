---
title: The extension host
description: Use VS Code's extension API in a test, to prepare it and to wait for a state, with Evaluate In Extension Host.
sidebar:
  order: 3
---

VS Code runs the extensions of a workbench window in a process of their own, the extension host. There, the `vscode` module gives access to VS Code's extension API. `Evaluate In Extension Host` runs a JavaScript function in the extension host and returns the function's result, the way `Evaluate In Main Process` does for VS Code's main process.

## When to use it

Use the API to prepare a test and to wait for a state:

- **Prepare:** run a command by its id instead of its title in the command palette, or open a file.
- **Wait:** until an extension is active, or until a language server has published the diagnostics of a file.
- **Read:** the text of an editor or the diagnostics of a file.

Check the outcome through the workbench, as a user sees it. A test that checks only through the API no longer tests what the user gets.

## Loading the helper extension

The keyword works through a small helper extension of the library. It listens on `127.0.0.1` with a random port, and accepts only requests with a token, which it writes into the instance's user-data directory.

The library does not load the helper: like the extensions under test, it is part of the test environment, which is set before VS Code starts. The `VSCode` package contains it twice, next to the library's `__init__.py`: as the folder `extension` and as the file `extension-host.vsix`. A test loads it in one of two ways. The helper is not in the Marketplace: it runs any function that a test sends, and it belongs to its version of the library.

### As a development extension

Give the folder to `Start VS Code` in `extension_development_path`, after your own extensions. Inline Python finds the folder in the installed package, also in a `*** Variables ***` section:

```robotframework
*** Variables ***
${HELPER_EXTENSION}    ${{ pathlib.Path(VSCode.__file__).parent / 'extension' }}

*** Test Cases ***
Refresh Command
    VAR    @{development}    ${EXECDIR}    ${HELPER_EXTENSION}
    Start VS Code    ${VSCODE_EXECUTABLE}    ${EXECDIR}/tests/workspace    extension_development_path=${development}
    Evaluate In Extension Host    (vscode) => vscode.commands.executeCommand('myExtension.refresh')
```

Nothing is installed, so this works with the fresh directories of every instance, and the folder always fits the installed library. The window becomes an "Extension Development Host": its title starts with `[Extension Development Host]`, also without an extension of your own, and `vscode.extensions.all` lists the helper, as `robotframework-vscode.extension-host`.

### Installed from the .vsix

Install `extension-host.vsix` into an extensions directory before VS Code starts, and give the directory to `Start VS Code` as `extensions_dir`. VS Code then runs without development mode. In Robot Framework, `Execute VS Code CLI Command` with `executable` installs it:

```robotframework
*** Settings ***
Library    VSCode

*** Variables ***
${HELPER_VSIX}    ${{ pathlib.Path(VSCode.__file__).parent / 'extension-host.vsix' }}
${PREPARED}       ${OUTPUT_DIR}/prepared

*** Test Cases ***
Installed Helper
    Execute VS Code CLI Command    --install-extension    ${HELPER_VSIX}
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${PREPARED}/extensions
    Start VS Code    ${VSCODE_EXECUTABLE}    extensions_dir=${PREPARED}/extensions
    ${version} =    Evaluate In Extension Host    (vscode) => vscode.version
```

In a shell, for example in a CI step that prepares the extensions directory before the tests, Python prints the path of the `.vsix`, and the command-line script of the VS Code that the tests start installs it: `bin/code` in the folder of a build that `@vscode/test-electron` downloaded. Run it outside VS Code's integrated terminal, where the script would talk to the VS Code that the terminal belongs to. `${vsix:?}` stops the command when Python does not find the library: with an empty value, the script ignores `--install-extension` and opens a VS Code window instead.

```bash
vsix=$(python -c "import pathlib, VSCode; print(pathlib.Path(VSCode.__file__).parent / 'extension-host.vsix')")
.vscode-test/vscode-linux-x64-1.141.0/bin/code --extensions-dir prepared/extensions --user-data-dir prepared/user-data \
    --install-extension "${vsix:?}"
```

The helper has the version of the library. After an update of the library, install the `.vsix` again, which replaces the old helper: until then, `Evaluate In Extension Host` fails at once with a message that names both versions.

## The function

The function gets the `vscode` module and `arg`, a value from the test. The keyword waits for a promise that the function returns, and returns its result:

```robotframework
${version} =    Evaluate In Extension Host    (vscode) => vscode.version
${text} =    Evaluate In Extension Host    (vscode) => vscode.window.activeTextEditor?.document.getText()
```

Further arguments continue the function, so that it can span several lines:

```robotframework
${lines} =    Evaluate In Extension Host    async (vscode, path) => {
...        const document = await vscode.workspace.openTextDocument(path);
...        await vscode.window.showTextDocument(document);
...        return document.lineCount;
...    }
...    arg=${EXECDIR}/tests/workspace/src/example.py
```

`arg` and the result travel as JSON. Objects of the API arrive as whatever JSON makes of them: a `TextEditor`, for example, as some of its properties, and a returned function as `None`. Return the values you need instead.

## Commands

`executeCommand` runs a command by its id. Its promise settles when the command has finished:

```robotframework
Evaluate In Extension Host    (vscode) => vscode.commands.executeCommand('robotTest.sayHello')
Wait For Elements State    .notifications-toasts .notification-list-item-message >> text="Hello Robot"    visible
```

A command that opens a quick pick or an input box finishes only once it is answered, so the keyword would wait until its timeout. Start such a command with `void`, and answer it through the workbench. The keyword then returns before the quick pick shows, so wait for it before typing:

```robotframework
Evaluate In Extension Host    (vscode) => { void vscode.commands.executeCommand('workbench.action.quickOpen'); }
Wait For Elements State    .quick-input-widget    visible
Keyboard Input    type    example.py
Wait For Elements State    .quick-input-list .monaco-list-row[aria-label*="example.py"]    visible
Keyboard Key    press    Enter
```

## Waiting for a state

`activate` of an extension returns once the extension is active, so a test can wait for it before it uses the extension's commands. `activate` returns the extension's API, which is no JSON, so the function returns nothing:

```robotframework
Evaluate In Extension Host    async (vscode) => {
...        await vscode.extensions.getExtension('ms-python.python').activate();
...    }
```

For states without a promise, such as the diagnostics of a file, let Robot Framework repeat a keyword that checks them:

```robotframework
*** Test Cases ***
Language Server Reports An Error
    Wait Until Keyword Succeeds    20s    0.5s    File Should Have Diagnostics    ${EXECDIR}/tests/workspace/broken.json

*** Keywords ***
File Should Have Diagnostics
    [Arguments]    ${path}
    ${messages} =    Evaluate In Extension Host    (vscode, path) =>
    ...    vscode.languages.getDiagnostics(vscode.Uri.file(path)).map((diagnostic) => diagnostic.message)
    ...    arg=${path}
    Should Not Be Empty    ${messages}
```

## Several windows

Each workbench window has its own extension host. Without `workspace`, the keyword takes the one of the window that shows the active page. `Switch Window` changes the window, and the keyword waits until the new window's extension host answers:

```robotframework
Evaluate In Extension Host    (vscode, path) => {
...        void vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path), { forceNewWindow: true });
...    }
...    arg=${EXECDIR}/tests/second-workspace
Switch Window    NEW
${folder} =    Evaluate In Extension Host    (vscode) => vscode.workspace.workspaceFolders[0].uri.fsPath
```

`workspace` selects a window by the folder or the `.code-workspace` file that it has open, without switching pages:

```robotframework
${name} =    Evaluate In Extension Host    (vscode) => vscode.workspace.name    workspace=${EXECDIR}/tests/second-workspace
```

- **Editors in windows of their own** belong to the workbench window that they came from, and use its extension host.
- **Windows without a workspace** cannot be named by `workspace`. The keyword finds such a window through its page, but with several of them it cannot tell them apart and fails. Right after a second one opens, only the first one's extension host answers, and the keyword runs the function there. For tests with several windows, open folders.
- **Several instances:** the keyword works on the active instance; `Switch Electron Application` changes it.

## Timeout

The keyword waits up to the library's timeout, which the import argument `timeout` and `Set Browser Timeout` set:

- **For the extension host:** right after `Start VS Code`, the extension host needs a moment to start. After the window reloads, the keyword waits for the new extension host. A reload takes a moment to begin, though: a function that a test evaluates right after starting one, for example with `workbench.action.reloadWindow`, can still run in the old extension host.
- **For the function:** a function that does not finish within the timeout keeps running in the extension host, because JavaScript cannot stop it. The keyword fails, but what the function does afterwards still happens.

## Things to know

- **The main process is another process.** `Evaluate In Main Process` runs in VS Code's main process, with Electron's API. The extension API exists only in the extension host.
- **Only local extension hosts.** Windows on a remote machine, in WSL or in a container run their extensions elsewhere, and the keyword does not reach them.
- **`arg=` in the function.** A cell that starts with `arg=` or `workspace=` is taken as that argument of the keyword, not as a line of the function. Write such a line with a space before `=`.
