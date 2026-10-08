*** Settings ***
Name                Open VS Code
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Workbench Is Ready
    Open Test VS Code
    Get Element States    .monaco-workbench    contains    visible
    Get Title    *=    Visual Studio Code

Local Installation
    ${code} =    Download VS Code    ${VSCODE_VERSION}    cache_dir=${VSCODE_CACHE}
    Open VS Code    executable=${code}    cache_dir=${TEMPDIR}/vscode-never-downloaded
    Get Title    *=    Visual Studio Code
    Directory Should Not Exist    ${TEMPDIR}/vscode-never-downloaded

Development Extension Is Active
    Open Test VS Code    extension_development_path=${TEST_EXTENSION}
    Keyboard Key    press    F1
    Keyboard Input    type    Robot Test: Say Hello
    Get Text    .quick-input-list .monaco-list-row[aria-label*="Robot Test: Say Hello"]    *=    Say Hello
    Keyboard Key    press    Enter
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot

Folder
    Open Test VS Code    ${TEST_WORKSPACE}
    Get Title    *=    workspace
