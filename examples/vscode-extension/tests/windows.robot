*** Settings ***
Documentation       Opens a second VS Code window and switches between the windows.

Library             OperatingSystem
Resource            resources/vscode.resource

Suite Setup         Start Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Second Window
    ${workspace} =    Example Workspace
    ${_}    ${folder} =    Split Path    ${workspace}
    # A shortcut avoids the palette, where "New Window" also matches "New Window with Profile".
    Keyboard Key    press    ControlOrMeta+Shift+n
    # The new window has no folder, so its title is VS Code's name, after the mark of the development host.
    Switch Window    title=[Extension Development Host] Visual Studio Code
    Wait For Elements State    .monaco-workbench    visible
    Get Title    not contains    ${folder}
    ${windows} =    Get Window Ids
    Length Should Be    ${windows}    2
    Close Page
    Get Title    contains    ${folder}
