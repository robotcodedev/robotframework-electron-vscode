*** Settings ***
Name        Helper
Library     OperatingSystem
Library     VSCode.Helper
Library     resources/VSCodeFixture.py
Resource    resources/variables.resource


*** Variables ***
${DIRECTORIES}      ${OUTPUT_DIR}/helper


*** Test Cases ***
Executable From The Helper
    ${code} =    Get VS Code Executable    ${VSCODE_VERSION}    ${VSCODE_EXECUTABLE}    ${VSCODE_CACHE}
    File Should Exist    ${code}

Extension Installed Into Given Directories
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${DIRECTORIES}/test-extension.vsix
    ${before} =    List User Extensions
    Execute VS Code CLI Command In Test Directories    --install-extension    ${vsix}
    ${list} =    Execute VS Code CLI Command In Test Directories    --list-extensions
    Should Contain    ${list}    robot.test-extension
    ${installed} =    List Directories In Directory    ${DIRECTORIES}/extensions    robot.test-extension-*
    Length Should Be    ${installed}    1
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Unknown Extension
    Run Keyword And Expect Error    VS Code's command line failed: *Extension 'robot.does-not-exist' not found*
    ...    Execute VS Code CLI Command In Test Directories    --install-extension    robot.does-not-exist


*** Keywords ***
Execute VS Code CLI Command In Test Directories
    [Arguments]    @{args}
    ${output} =    Execute VS Code CLI Command    ${DIRECTORIES}/extensions    ${DIRECTORIES}/user-data    @{args}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
    RETURN    ${output}
