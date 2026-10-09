*** Settings ***
Documentation       Opens files of the workspace, edits one and saves it.

Library             OperatingSystem
Resource            resources/vscode.resource
Resource            resources/editor.resource
Resource            resources/file_dialog.resource

Suite Setup         Open Example VS Code
Suite Teardown      Close VS Code


*** Test Cases ***
Edit And Save A File
    Open File    notes.txt
    Keyboard Key    press    ControlOrMeta+End
    Keyboard Input    type    Edited by Robot Framework
    Save File
    Take Screenshot    filename=editor
    ${workspace} =    Example Workspace
    Wait Until Keyword Succeeds    5s    200ms    File Should Contain    ${workspace}/notes.txt    Edited by Robot Framework

Open A File With The Dialog
    ${workspace} =    Example Workspace
    Open File With Dialog    ${workspace}/hello.py
    Active Editor Should Be    hello.py


*** Keywords ***
File Should Contain
    [Arguments]    ${path}    ${text}
    ${content} =    Get File    ${path}
    Should Contain    ${content}    ${text}
