*** Settings ***
Documentation       Runs a command of the extension through the command palette.

Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/notifications.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Command Shows A Notification
    Run Command    Robot Example: Say Hello
    Notification Should Be Shown    Hello Robot
