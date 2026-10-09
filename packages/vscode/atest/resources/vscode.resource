*** Settings ***
Library     VSCode
Library     VSCode.Helper
Library     VSCodeFixture.py
Resource    variables.resource


*** Keywords ***
Open Test VS Code
    [Arguments]    @{args}    &{options}
    ${ids} =    Open VS Code    @{args}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}    &{options}
    RETURN    ${ids}

Newest Instance
    ${instance} =    Newest Instance Directory    ${OUTPUT_DIR}
    RETURN    ${instance}

VS Code Instance Is Running
    [Arguments]    ${instance}
    ${processes} =    Count Processes With    --user-data-dir=${instance}/user-data
    Should Be True    ${processes} > 0

VS Code Instance Has Exited
    [Arguments]    ${instance}
    ${processes} =    Count Processes With    --user-data-dir=${instance}/user-data
    Should Be Equal As Integers    ${processes}    0

Run Command From A Fresh Palette
    [Arguments]    ${title}
    Keyboard Key    press    Escape
    Keyboard Key    press    F1
    Keyboard Input    type    ${title}
    Wait For Elements State    .quick-input-list .monaco-list-row[aria-label*="${title}"]    visible    timeout=2s
    Keyboard Key    press    Enter
