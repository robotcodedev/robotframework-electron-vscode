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
    Execute VS Code CLI Command    --install-extension    editorconfig.editorconfig
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${prepared}/extensions
    Start Test VS Code    extensions_dir=${prepared}/extensions
    ${dirs} =    Get VS Code Instance Directories
    ${installed} =    List Directories In Directory    ${dirs.extensions}    editorconfig.editorconfig-*
    Length Should Be    ${installed}    1
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Setting Takes Effect
    Start Test VS Code    settings=${{ {"window.title": "robot-test"} }}
    Get Title    ==    robot-test

Quiet Start
    Start Test VS Code    ${TEST_WORKSPACE}
    Wait For Elements State    .explorer-folders-view    visible
    Get Element Count    .tabs-container .tab    ==    0
    Get Element Count    .monaco-dialog-box    ==    0

Two Instances
    ${first}    ${_} =    Start Test VS Code
    ${first_instance} =    Newest Instance
    Start Test VS Code
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
    Start Test VS Code
    ${instance} =    Newest Instance
    VS Code Instance Is Running    ${instance}
    ${extensions} =    List Directories In Directory    ${instance}/extensions
    Should Be Empty    ${extensions}

Logs After A Failed Test
    [Tags]    vscode-only
    Start Test VS Code
    ${instance} =    Newest Instance
    Close VS Code
    Directory Should Not Be Empty    ${instance}/user-data/logs

Directories Of The Active Instance
    Start Test VS Code
    ${instance} =    Newest Instance
    ${dirs} =    Get VS Code Instance Directories
    Should Be Equal    ${dirs.root}    ${instance}
    Should Be Equal    ${dirs.user_data}    ${instance}/user-data
    Should Be Equal    ${dirs}[extensions]    ${instance}/extensions

Directories With Given Directories
    ${vscode}    ${_} =    Start Test VS Code
    ...    extensions_dir=${OUTPUT_DIR}/given-extensions    user_data_dir=${OUTPUT_DIR}/given-user-data
    Start Test VS Code
    ${dirs} =    Get VS Code Instance Directories    ${vscode}
    Should Be Equal    ${dirs.extensions}    ${OUTPUT_DIR}/given-extensions
    Should Be Equal    ${dirs.user_data}    ${OUTPUT_DIR}/given-user-data

Prepared User Data
    VAR    ${prepared}    ${OUTPUT_DIR}/prepared-user-data
    Remove Directory    ${prepared}    recursive=True
    Create File    ${prepared}/User/settings.json    {"window.title": "prepared"}
    Start Test VS Code    user_data_dir=${prepared}
    Get Title    ==    prepared
    ${dirs} =    Get VS Code Instance Directories
    Should Be Equal    ${dirs.user_data}    ${prepared}
    Should Be Equal    ${dirs.extensions}    ${dirs.root}${/}extensions
    Directory Should Be Empty    ${dirs.extensions}

Settings With A Given User-Data Directory
    VAR    ${prepared}    ${OUTPUT_DIR}/given-user-data-and-settings
    Remove Directory    ${prepared}    recursive=True
    Create Directory    ${prepared}
    Run Keyword And Expect Error    ValueError: 'settings' cannot be combined with 'user_data_dir'*
    ...    Start Test VS Code    user_data_dir=${prepared}    settings=${{ {"window.title": "robot-test"} }}
    Directory Should Be Empty    ${prepared}
    ${ids} =    Get Electron Application Ids
    Should Be Empty    ${ids}

Directories Of An Id Not Returned By Start VS Code
    Run Keyword And Expect Error    *'browser=unknown' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    browser=unknown

Directories Of A Closed Instance
    ${vscode}    ${_} =    Start Test VS Code
    Close VS Code    ${vscode}
    Run Keyword And Expect Error    *'${vscode}' is not an open VS Code instance*
    ...    Get VS Code Instance Directories    ${vscode}
