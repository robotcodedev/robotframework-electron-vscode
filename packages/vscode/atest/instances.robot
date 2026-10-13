*** Settings ***
Name                Instances
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


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
    # The library's helper extension makes the window an Extension Development Host.
    Get Title    ==    [Extension Development Host] robot-test

Quiet Start
    Open Test VS Code    ${TEST_WORKSPACE}
    Wait For Elements State    .explorer-folders-view    visible
    Get Element Count    .tabs-container .tab    ==    0
    Get Element Count    .monaco-dialog-box    ==    0

Two Instances
    ${first}    ${_} =    Open Test VS Code
    ${first_instance} =    Newest Instance
    Open Test VS Code
    ${second_instance} =    Newest Instance
    VS Code Instance Is Running    ${first_instance}
    VS Code Instance Is Running    ${second_instance}
    ${ids} =    Get Electron Application Ids
    Length Should Be    ${ids}    2
    Switch Electron Application    ${first}
    Get Element States    .monaco-workbench    contains    visible
    Close VS Code
    VS Code Instance Has Exited    ${first_instance}
    VS Code Instance Is Running    ${second_instance}
    Close VS Code    ALL
    VS Code Instance Has Exited    ${second_instance}

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
    ${vscode}    ${_} =    Open Test VS Code    extensions_dir=${OUTPUT_DIR}/given-extensions
    Open Test VS Code
    ${dirs} =    Get VS Code Instance Directories    ${vscode}
    Should Be Equal    ${dirs.extensions}    ${OUTPUT_DIR}/given-extensions

Directories Of An Id Not Returned By Open VS Code
    Run Keyword And Expect Error    *'browser=unknown' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    browser=unknown

Directories Of A Closed Instance
    ${vscode}    ${_} =    Open Test VS Code
    Close VS Code    ${vscode}
    Run Keyword And Expect Error    *'${vscode}' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    ${vscode}
