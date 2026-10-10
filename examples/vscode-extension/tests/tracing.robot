*** Settings ***
Documentation       Records a Playwright trace of each test and a HAR file of the workbench's network traffic.
...
...                 The traces are saved in `browser/traces` in the output directory when VS Code
...                 closes at the end of a test. Open one with `rfbrowser show-trace <file>`.

Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/notifications.resource
Resource            resources/webview.resource


*** Test Cases ***
Trace Of A Command
    Open Example VS Code    tracing=${True}
    Run Command    Robot Example: Say Hello
    Notification Should Be Shown    Hello Robot

Trace Of A Webview With The Network Traffic
    Open Example VS Code    tracing=${True}    record_har=${{ {"path": "har/webview.har"} }}
    Run Command    Robot Example: Open Webview
    ${previous} =    Enter Webview    robot.example-extension
    Click    id=click-me
    Get Text    id=status    ==    Clicked
    Leave Webview    ${previous}
