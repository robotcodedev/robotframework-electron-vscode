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

Open Test VS Code With Helper
    [Documentation]    Opens VS Code with the library's helper extension after the given development extensions.
    [Arguments]    @{args}    ${extension_development_path}=${NONE}    &{options}
    VAR    @{development}    ${HELPER_EXTENSION}
    IF    $extension_development_path is not None
        VAR    @{development}    ${extension_development_path}    ${HELPER_EXTENSION}
    END
    ${ids} =    Open Test VS Code    @{args}    extension_development_path=${development}    &{options}
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
    [Arguments]    ${extension}    ${id}
    ${dirs} =    Get VS Code Instance Directories
    # VS Code's shared process can still be starting while the workbench shows, and then misses an extension
    # that arrives, or deletes it again. The extension host comes up later.
    Evaluate In Extension Host    () => true
    # The running instance writes extensions.json as well, so the script can fail on a busy file once.
    Wait Until Keyword Succeeds    2x    1s
    ...    Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    ${extension}
    ${known} =    Run Keyword And Return Status    Wait Until Keyword Succeeds    10s    0.2s
    ...    Extension Host Should Know    ${id}
    IF    not ${known}
        # Brings back a deleted extension; the reload makes the window read its extensions anew.
        Run Keyword And Ignore Error
        ...    Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --uninstall-extension    ${id}
        Execute Test VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    ${extension}
        Evaluate In Extension Host
        ...    (vscode) => { void vscode.commands.executeCommand('workbench.action.reloadWindow'); }
        Wait Until Keyword Succeeds    30s    0.5s    Extension Host Should Know    ${id}
    END

Extension Host Should Know
    [Arguments]    ${id}
    ${known} =    Evaluate In Extension Host    (vscode, id) => vscode.extensions.getExtension(id) !== undefined
    ...    arg=${id}
    Should Be True    ${known}    The extension host does not know ${id}.
