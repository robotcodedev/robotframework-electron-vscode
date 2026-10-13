*** Settings ***
Name                Extension Host
Documentation       Evaluate In Extension Host runs functions with VS Code's extension API in the extension
...                 host of a window. The first tests share an instance; the later ones need instances of
...                 their own.
Resource            resources/vscode.resource

Suite Setup         Open Test VS Code With Helper    ${TEST_WORKSPACE}    extension_development_path=${TEST_EXTENSION}
Suite Teardown      Close VS Code    ALL


*** Variables ***
${SECOND_WORKSPACE}     ${OUTPUT_DIR}${/}second-workspace


*** Test Cases ***
VS Code's Version From The Extension Host
    ${version} =    Evaluate In Extension Host    (vscode) => vscode.version
    # The profile vscode-insiders sets the version to "insiders", whose number changes with every build,
    # and a local VS Code from VSCODE_EXECUTABLE has its own version.
    IF    $VSCODE_EXECUTABLE is None and $VSCODE_VERSION[0].isdigit()
        Should Be Equal    ${version}    ${VSCODE_VERSION}
    ELSE
        Should Match Regexp    ${version}    ^\\d+\\.\\d+\\.\\d+
    END

Command By Its Id
    Evaluate In Extension Host    (vscode) => vscode.commands.executeCommand('robotTest.sayHello')
    # VS Code may also show a notification about the git repository around the workspace.
    Get Text    .notifications-toasts .notification-list-item-message:has-text("Hello Robot")    ==    Hello Robot
    [Teardown]    Evaluate In Extension Host    (vscode) => vscode.commands.executeCommand('notifications.clearAll')

Function Over Several Lines With An Argument
    ${result} =    Evaluate In Extension Host    (vscode, arg) => {
    ...        const total = arg.numbers.reduce((sum, number) => sum + number, 0);
    ...        return arg.name + ': ' + total;
    ...    }
    ...    arg=${{ {"name": "sum", "numbers": [1, 2, 3]} }}
    Should Be Equal    ${result}    sum: 6

Text Of The Active Editor
    VAR    ${file} =    ${TEST_WORKSPACE}${/}src${/}example.txt
    Evaluate In Extension Host    async (vscode, path) => {
    ...        await vscode.window.showTextDocument(vscode.Uri.file(path));
    ...    }
    ...    arg=${file}
    Get Title    contains    example.txt
    ${text} =    Evaluate In Extension Host    (vscode) => vscode.window.activeTextEditor.document.getText()
    ${expected} =    Get File    ${file}
    Should Be Equal    ${text}    ${expected}
    [Teardown]    Evaluate In Extension Host
    ...    (vscode) => vscode.commands.executeCommand('workbench.action.closeAllEditors')

Function Throws
    Run Keyword And Expect Error    EQUALS:broken
    ...    Evaluate In Extension Host    () => { throw new Error('broken'); }

Promise Rejects
    Run Keyword And Expect Error    EQUALS:rejected
    ...    Evaluate In Extension Host    async () => { throw new Error('rejected'); }

Result That Is No JSON
    Run Keyword And Expect Error    The function's result cannot be serialised as JSON: *
    ...    Evaluate In Extension Host    () => 10n

Evaluation Does Not Finish
    Set Browser Timeout    1s    scope=Test
    Run Keyword And Expect Error    The function did not finish within 1 second.*
    ...    Evaluate In Extension Host    () => new Promise(() => {})

As A Development Extension Next To The Extension Under Test
    ${commands} =    Evaluate In Extension Host    async (vscode) => {
    ...        const commands = await vscode.commands.getCommands(true);
    ...        return commands.includes('robotTest.sayHello');
    ...    }
    Should Be True    ${commands}
    ${arguments} =    Evaluate In Main Process    () => process.argv
    ${paths} =    Evaluate    [arg for arg in $arguments if arg.startswith("--extensionDevelopmentPath=")]
    Length Should Be    ${paths}    2

Request Without The Token
    Evaluate In Extension Host    () => { globalThis.robotTokenTest = 'untouched'; }
    ${dirs} =    Get VS Code Instance Directories
    ${statuses} =    Send Evaluation Without Token    ${dirs.user_data}    () => { globalThis.robotTokenTest = 'ran'; }
    Should Be Equal    ${statuses}    ${{ [403] }}
    ${value} =    Evaluate In Extension Host    () => globalThis.robotTokenTest
    Should Be Equal    ${value}    untouched

Workspace That No Window Has Open
    Set Browser Timeout    2s    scope=Test
    VAR    ${nowhere} =    ${OUTPUT_DIR}${/}nowhere
    Run Keyword And Expect Error
    ...    EQUALS:No window of the VS Code instance has the workspace '${nowhere}' open within 2 seconds. Open workspaces: '${TEST_WORKSPACE}'.
    ...    Evaluate In Extension Host    () => 1    workspace=${nowhere}

Right After The Start
    ${vscode}    ${_} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    ${name} =    Evaluate In Extension Host    (vscode) => vscode.env.appName
    Should Not Be Empty    ${name}
    [Teardown]    Close VS Code    ${vscode}

Without An Extension Under Test
    ${vscode}    ${_} =    Open Test VS Code With Helper
    ${helper} =    Evaluate In Extension Host
    ...    (vscode) => vscode.extensions.all.filter((extension) => !extension.packageJSON.isBuiltin).map((e) => e.id)
    Should Be Equal    ${helper}    ${{ ["robotframework-vscode.extension-host"] }}
    Get Title    ^=    [Extension Development Host]
    [Teardown]    Close VS Code    ${vscode}

After The Window Reloads
    ${vscode}    ${_} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    ${before} =    Evaluate In Extension Host    () => process.pid
    Evaluate In Extension Host
    ...    (vscode) => { void vscode.commands.executeCommand('workbench.action.reloadWindow'); }
    # The keyword waits for an extension host, not for a reload that is about to begin.
    Wait Until Keyword Succeeds    30s    0.05s    Process Should Have Exited    ${before}
    ${after} =    Evaluate In Extension Host    () => process.pid
    Should Not Be Equal    ${after}    ${before}
    [Teardown]    Close VS Code    ${vscode}

Window By Its Workspace
    ${vscode}    ${_} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    Open Folder In New Window    ${SECOND_WORKSPACE}
    ${folder} =    Evaluate In Extension Host    (vscode) => vscode.workspace.workspaceFolders[0].uri.fsPath
    ...    workspace=${SECOND_WORKSPACE}
    Should Be Equal    ${folder}    ${SECOND_WORKSPACE}
    [Teardown]    Close VS Code    ${vscode}

Window Of The Active Page
    ${vscode}    ${first} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    Open Folder In New Window    ${SECOND_WORKSPACE}
    Wait Until The Extension Host Answers    ${SECOND_WORKSPACE}
    Folder Of The Active Pages Window Should Be    ${TEST_WORKSPACE}
    Switch Page    NEW
    Folder Of The Active Pages Window Should Be    ${SECOND_WORKSPACE}
    # The page of this instance's first window, not one of the suite's instance.
    Switch Page    ${first}[page_id]
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$vscode] }}
    Folder Of The Active Pages Window Should Be    ${TEST_WORKSPACE}
    [Teardown]    Close VS Code    ${vscode}

Window That Has Just Opened
    ${vscode}    ${_} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    Open Folder In New Window    ${SECOND_WORKSPACE}
    Switch Page    NEW
    Folder Of The Active Pages Window Should Be    ${SECOND_WORKSPACE}
    [Teardown]    Close VS Code    ${vscode}

Editor Moved Into Its Own Window
    ${vscode}    ${_} =    Open Test VS Code With Helper    ${TEST_WORKSPACE}
    Evaluate In Extension Host    async (vscode, path) => {
    ...        await vscode.window.showTextDocument(vscode.Uri.file(path));
    ...        void vscode.commands.executeCommand('workbench.action.moveEditorToNewWindow');
    ...    }
    ...    arg=${TEST_WORKSPACE}${/}src${/}example.txt
    Switch Page    NEW
    Get Title    contains    example.txt
    Open Folder In New Window    ${SECOND_WORKSPACE}
    Wait Until The Extension Host Answers    ${SECOND_WORKSPACE}
    Folder Of The Active Pages Window Should Be    ${TEST_WORKSPACE}
    [Teardown]    Close VS Code    ${vscode}

Several Windows Without A Workspace
    ${vscode}    ${_} =    Open Test VS Code With Helper
    Evaluate In Extension Host    (vscode) => { void vscode.commands.executeCommand('workbench.action.newWindow'); }
    Switch Page    NEW
    # Until the new window's extension host answers, the first one is the only one.
    Wait Until Keyword Succeeds    30s    0.5s
    ...    Run Keyword And Expect Error    The window of the active page cannot be determined: *
    ...    Evaluate In Extension Host    () => 1
    [Teardown]    Close VS Code    ${vscode}

Application That Is Not A VS Code Instance
    ${code} =    Get VS Code Executable    ${VSCODE_VERSION}    ${VSCODE_EXECUTABLE}    ${VSCODE_CACHE}
    ${environment} =    VS Code Environment
    VAR    ${folder} =    ${OUTPUT_DIR}${/}plain-vs-code
    ${app}    ${_} =    New Electron Application    ${code}
    ...    args=${{ ["--user-data-dir=" + $folder + "/user-data", "--extensions-dir=" + $folder + "/extensions"] }}
    ...    env=${environment}
    Run Keyword And Expect Error    EQUALS:'${app}' is not an open VS Code instance started by 'Open VS Code'.
    ...    Evaluate In Extension Host    () => 1
    [Teardown]    Close Electron Application    ${app}

No VS Code Instance Open
    Close VS Code    ALL
    Run Keyword And Expect Error    EQUALS:No VS Code instance is open.
    ...    Evaluate In Extension Host    () => 1


*** Keywords ***
Open Folder In New Window
    [Arguments]    ${folder}
    Create Directory    ${folder}
    Evaluate In Extension Host    (vscode, path) => {
    ...        const uri = vscode.Uri.file(path);
    ...        void vscode.commands.executeCommand('vscode.openFolder', uri, { forceNewWindow: true });
    ...    }
    ...    arg=${folder}

Wait Until The Extension Host Answers
    [Arguments]    ${workspace}
    Evaluate In Extension Host    () => true    workspace=${workspace}

Folder Of The Active Pages Window Should Be
    [Arguments]    ${expected}
    ${folder} =    Evaluate In Extension Host    (vscode) => vscode.workspace.workspaceFolders[0].uri.fsPath
    Should Be Equal    ${folder}    ${expected}
