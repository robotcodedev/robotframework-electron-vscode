*** Settings ***
Library     VSCode
Library     VSCodeFixture.py


*** Variables ***
${VSCODE_VERSION}       1.141.0
${VSCODE_EXECUTABLE}    ${NONE}
${VSCODE_CACHE}         ${EXECDIR}/.cache/vscode
${TEST_EXTENSION}       ${EXECDIR}/packages/vscode/atest/fixtures/extension
${TEST_WORKSPACE}       ${EXECDIR}/packages/vscode/atest/fixtures/workspace


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
