*** Settings ***
Documentation       Selects an item in a quick pick that the extension shows.

Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/quick_pick.resource
Resource            resources/notifications.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Picked Item Reaches The Extension
    Run Command    Robot Example: Pick
    Quick Pick Item Should Be Shown    Banana
    Take Screenshot    filename=quick-pick
    Select Quick Pick Item    Banana
    Notification Should Be Shown    You picked Banana
