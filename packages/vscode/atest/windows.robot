*** Settings ***
Documentation       The window keywords of the Electron library on VS Code's workbench windows.
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
Second Workbench Window
    Start Test VS Code    ${TEST_WORKSPACE}
    # A shortcut avoids the palette, where "New Window" also matches "New Window with Profile".
    Keyboard Key    press    ControlOrMeta+Shift+n
    ${previous} =    Switch Window    title=Visual Studio Code
    Wait For Elements State    .monaco-workbench    visible
    Maximize Window
    Get Window State    ==    maximized
    ${titles} =    Get Window Titles
    Length Should Be    ${titles}    2
    Switch Window    ${previous}
    Get Window State    ==    normal
