*** Settings ***
Library     OperatingSystem
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

Execute Test VS Code CLI Command
    [Arguments]    ${extensions_dir}    ${user_data_dir}    @{args}
    ${output} =    Execute VS Code CLI Command    ${extensions_dir}    ${user_data_dir}    @{args}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
    RETURN    ${output}

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

Install Into Running Instance
    [Arguments]    ${extension}    ${id}    ${browser}=CURRENT
    ${dirs} =    Get VS Code Instance Directories    ${browser}
    # The running instance writes extensions.json as well, so the script can fail on a busy file once.
    Wait Until Keyword Succeeds    2x    1s
    ...    Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    ${extension}
    ${reported} =    Run Keyword And Return Status    Wait Until Keyword Succeeds    10s    0.2s
    ...    Shared Process Log Should Contain    ${dirs.user_data}    Extensions added from another source ${id}
    IF    not ${reported}
        # VS Code misses an install while it is still starting. Installing again makes it notice.
        Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --uninstall-extension    ${id}
        Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    ${extension}
        Wait Until Keyword Succeeds    10s    0.2s
        ...    Shared Process Log Should Contain    ${dirs.user_data}    Extensions added from another source ${id}
    END

Shared Process Log Should Contain
    [Arguments]    ${user_data_dir}    ${text}
    # Calls of the command-line script add log folders of their own, without sharedprocess.log.
    ${logs} =    Evaluate    sorted(pathlib.Path($user_data_dir, "logs").glob("*/sharedprocess.log"))    modules=pathlib
    ${log} =    Get File    ${logs}[-1]
    Should Contain    ${log}    ${text}
