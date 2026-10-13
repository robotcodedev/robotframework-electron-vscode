---
title: The extension host
description: Use VS Code's extension API in a test, to prepare it and to wait for a state, with Evaluate In Extension Host.
---

VS Code runs the extensions of a workbench window in a process of their own, the extension host. There, the `vscode` module gives access to VS Code's extension API. `Evaluate In Extension Host` runs a JavaScript function in the extension host and returns the function's result, the way `Evaluate In Main Process` does for VS Code's main process.

## When to use it

Use the API to prepare a test and to wait for a state:

- **Prepare:** run a command by its id instead of its title in the command palette, or open a file.
- **Wait:** until an extension is active, or until a language server has published the diagnostics of a file.
- **Read:** the text of an editor or the diagnostics of a file.

Check the outcome through the workbench, as a user sees it. A test that checks only through the API no longer tests what the user gets.

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

Each workbench window has its own extension host. Without `workspace`, the keyword takes the one of the window that shows the active page. `Switch Page` changes the window, and the keyword waits until the new window's extension host answers:

```robotframework
Evaluate In Extension Host    (vscode, path) => {
...        void vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(path), { forceNewWindow: true });
...    }
...    arg=${EXECDIR}/tests/second-workspace
Switch Page    NEW
${folder} =    Evaluate In Extension Host    (vscode) => vscode.workspace.workspaceFolders[0].uri.fsPath
```

`workspace` selects a window by the folder or the `.code-workspace` file that it has open, without switching pages:

```robotframework
${name} =    Evaluate In Extension Host    (vscode) => vscode.workspace.name    workspace=${EXECDIR}/tests/second-workspace
```

- **Editors in windows of their own** belong to the workbench window that they came from, and use its extension host.
- **Windows without a workspace** cannot be named by `workspace`. The keyword finds such a window through its page, but with several of them it cannot tell them apart and fails. Right after a second one opens, only the first one's extension host answers, and the keyword runs the function there. For tests with several windows, open folders.
- **Several instances:** the keyword works on the active instance; `Switch Electron Application` changes it.

## The helper extension

The keyword works through a small helper extension of the library. `Open VS Code` loads it as an additional development extension. The helper listens on `127.0.0.1` with a random port, and accepts only requests with a token, which it writes into the instance's user-data directory.

The helper has two effects that a test can notice:

- The window is an "Extension Development Host", and its title starts with `[Extension Development Host]`, also without an extension of your own in `extension_development_path`.
- `vscode.extensions.all` lists the helper, as `robotframework-vscode.extension-host`.

Where that matters, the import argument `enable_extension_host_evaluation` switches the helper off. `Evaluate In Extension Host` then fails with a message that names the argument:

```robotframework
*** Settings ***
Library    VSCode    enable_extension_host_evaluation=False
```

## Timeout

The keyword waits up to the library's timeout, which the import argument `timeout` and `Set Browser Timeout` set:

- **For the extension host:** right after `Open VS Code`, the extension host needs a moment to start. After the window reloads, the keyword waits for the new extension host. A reload takes a moment to begin, though: a function that a test evaluates right after starting one, for example with `workbench.action.reloadWindow`, can still run in the old extension host.
- **For the function:** a function that does not finish within the timeout keeps running in the extension host, because JavaScript cannot stop it. The keyword fails, but what the function does afterwards still happens.

## Things to know

- **The main process is another process.** `Evaluate In Main Process` runs in VS Code's main process, with Electron's API. The extension API exists only in the extension host.
- **Only local extension hosts.** Windows on a remote machine, in WSL or in a container run their extensions elsewhere, and the keyword does not reach them.
- **`arg=` in the function.** A cell that starts with `arg=` or `workspace=` is taken as that argument of the keyword, not as a line of the function. Write such a line with a space before `=`.
