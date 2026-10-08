*** Settings ***
Name                Instances
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Marketplace Extension
    ${before} =    List User Extensions
    Open Test VS Code    extensions=${{ ["editorconfig.editorconfig"] }}
    ${instance} =    Newest Instance
    ${installed} =    List Directories In Directory    ${instance}/extensions    editorconfig.editorconfig-*
    Length Should Be    ${installed}    1
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Setting Takes Effect
    Open Test VS Code    settings=${{ {"window.title": "robot-test"} }}
    Get Title    ==    robot-test

Quiet Start
    Open Test VS Code    ${TEST_WORKSPACE}
    Wait For Elements State    .explorer-folders-view    visible
    Get Element Count    .tabs-container .tab    ==    0
    Get Element Count    .monaco-dialog-box    ==    0

Two Instances
    ${first}    ${_}    ${_} =    Open Test VS Code
    ${first_instance} =    Newest Instance
    Open Test VS Code
    ${second_instance} =    Newest Instance
    VS Code Instance Is Running    ${first_instance}
    VS Code Instance Is Running    ${second_instance}
    Close VS Code
    VS Code Instance Has Exited    ${second_instance}
    VS Code Instance Is Running    ${first_instance}
    Switch Browser    ${first}
    Get Element States    .monaco-workbench    contains    visible

User's VS Code Is Unaffected
    Open Test VS Code
    ${instance} =    Newest Instance
    VS Code Instance Is Running    ${instance}
    ${extensions} =    List Directories In Directory    ${instance}/extensions
    Should Be Empty    ${extensions}

Logs After A Failed Test
    [Tags]    vscode-only
    Open Test VS Code
    ${instance} =    Newest Instance
    Close VS Code
    Directory Should Not Be Empty    ${instance}/user-data/logs
