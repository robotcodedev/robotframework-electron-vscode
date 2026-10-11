*** Settings ***
Name                Instances
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Marketplace Extension
    VAR    ${prepared}    ${OUTPUT_DIR}/marketplace
    Remove Directory    ${prepared}    recursive=True
    ${before} =    List User Extensions
    Execute Test VS Code CLI Command    ${prepared}/extensions    ${prepared}/user-data    --install-extension    editorconfig.editorconfig
    Open Test VS Code    extensions_dir=${prepared}/extensions
    ${dirs} =    Get VS Code Instance Directories
    ${installed} =    List Directories In Directory    ${dirs.extensions}    editorconfig.editorconfig-*
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

Directories Of The Active Instance
    Open Test VS Code
    ${instance} =    Newest Instance
    ${dirs} =    Get VS Code Instance Directories
    Should Be Equal    ${dirs.root}    ${instance}
    Should Be Equal    ${dirs.user_data}    ${instance}/user-data
    Should Be Equal    ${dirs}[extensions]    ${instance}/extensions

Directories With A Given Extensions Directory
    ${vscode}    ${_}    ${_} =    Open Test VS Code    extensions_dir=${OUTPUT_DIR}/given-extensions
    Open Test VS Code
    ${dirs} =    Get VS Code Instance Directories    ${vscode}
    Should Be Equal    ${dirs.extensions}    ${OUTPUT_DIR}/given-extensions

Directories Of A Browser Not Opened By Open VS Code
    ${browser} =    New Browser    chromium    headless=True
    Run Keyword And Expect Error    *Browser '${browser}' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    ${browser}

Directories Of A Closed Instance
    ${vscode}    ${_}    ${_} =    Open Test VS Code
    Close VS Code    ${vscode}
    Run Keyword And Expect Error    *Browser '${vscode}' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    ${vscode}
