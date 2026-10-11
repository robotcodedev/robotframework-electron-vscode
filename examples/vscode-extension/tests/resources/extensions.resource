*** Settings ***
Documentation       Gets extensions into VS Code with VS Code's command-line script: prepared once and
...                 copied into each VS Code, or installed into the running VS Code.

Library             OperatingSystem
Library             VSCode
Library             VSCode.Helper
Resource            vscode.resource


*** Variables ***
# Where extensions are prepared once and kept for later runs, per VS Code version.
${PREPARED_EXTENSIONS}      ${EXECDIR}/.cache/extensions/${VSCODE_VERSION}


*** Keywords ***
Prepared Extensions
    [Documentation]    Returns a fresh copy of the prepared extensions directory for one VS Code.
    ...
    ...    The extensions are installed into `${PREPARED_EXTENSIONS}` on first use, with the
    ...    VS Code version the tests run against. Later calls, also in later runs, find
    ...    them there and download nothing. Each VS Code gets its own copy, because VS Code
    ...    writes into its extensions directory while it runs.
    [Arguments]    @{extensions}
    VAR    @{install}
    FOR    ${extension}    IN    @{extensions}
        VAR    @{install}    @{install}    --install-extension    ${extension}
    END
    Execute VS Code CLI Command    ${PREPARED_EXTENSIONS}/extensions    ${PREPARED_EXTENSIONS}/user-data    @{install}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
    VAR    ${copy}    ${OUTPUT_DIR}/extensions/${TEST NAME}
    Remove Directory    ${copy}    recursive=True
    Copy Directory    ${PREPARED_EXTENSIONS}/extensions    ${copy}
    RETURN    ${copy}

Install Into Running VS Code
    [Documentation]    Installs an extension into the active VS Code and waits until VS Code has taken it in.
    ...
    ...    VS Code's command-line script installs into the directories of the running
    ...    VS Code, and VS Code notices the new extension a moment later. Its shared
    ...    process reports that in its log. VS Code misses an install while it is still
    ...    starting, so if the report does not come, the keyword installs the extension
    ...    again. The script can also fail once because VS Code writes the list of
    ...    extensions at the same time, so the first install is tried twice.
    [Arguments]    ${extension}
    ${dirs} =    Get VS Code Instance Directories
    Wait Until Keyword Succeeds    2x    1s
    ...    Execute VS Code CLI Command In Instance    ${dirs}    --install-extension    ${extension}
    ${reported} =    Run Keyword And Return Status    Wait Until Keyword Succeeds    10s    0.2s
    ...    Shared Process Log Should Contain    ${dirs.user_data}    Extensions added from another source ${extension}
    IF    not ${reported}
        Execute VS Code CLI Command In Instance    ${dirs}    --uninstall-extension    ${extension}
        Execute VS Code CLI Command In Instance    ${dirs}    --install-extension    ${extension}
        Wait Until Keyword Succeeds    10s    0.2s
        ...    Shared Process Log Should Contain    ${dirs.user_data}    Extensions added from another source ${extension}
    END

Execute VS Code CLI Command In Instance
    [Documentation]    Runs VS Code's command-line script on the directories of a running VS Code.
    [Arguments]    ${dirs}    @{args}
    Execute VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    @{args}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}

Shared Process Log Should Contain
    [Documentation]    Fails unless the shared process log of the running VS Code contains the text.
    ...
    ...    The log is `sharedprocess.log` in the newest folder under `logs` of the user-data
    ...    directory that has one; calls of the command-line script add folders without it.
    [Arguments]    ${user_data_dir}    ${text}
    ${logs} =    Evaluate    sorted(pathlib.Path($user_data_dir, "logs").glob("*/sharedprocess.log"))    modules=pathlib
    ${log} =    Get File    ${logs}[-1]
    Should Contain    ${log}    ${text}
