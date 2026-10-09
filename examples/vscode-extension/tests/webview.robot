*** Settings ***
Documentation       Acts inside a webview of the extension and on the workbench afterwards.

Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/webview.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Button In The Webview
    Run Command    Robot Example: Open Webview
    ${previous} =    Enter Webview    robot.example-extension
    Get Text    id=status    ==    Not clicked
    Click    id=click-me
    Get Text    id=status    ==    Clicked
    Take Screenshot    filename=webview
    Leave Webview    ${previous}
    Get Text    .tabs-container .tab.active    *=    Robot Example
