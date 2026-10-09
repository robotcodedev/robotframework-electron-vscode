*** Settings ***
Documentation       Opens a second VS Code window and switches between the windows.

Library             OperatingSystem
Resource            resources/vscode.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Second Window
    ${workspace} =    Example Workspace
    ${_}    ${folder} =    Split Path    ${workspace}
    # A shortcut avoids the palette, where "New Window" also matches "New Window with Profile".
    Keyboard Key    press    ControlOrMeta+Shift+n
    Switch Page    NEW
    Wait For Elements State    .monaco-workbench    visible
    Get Title    not contains    ${folder}
    ${pages} =    Get Page Ids    ALL
    Length Should Be    ${pages}    2
    Close Page
    Get Title    contains    ${folder}
