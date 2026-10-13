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
    ...    VS Code. While VS Code's shared process is still starting, it misses an
    ...    extension that arrives, or even deletes it again, and the workbench can show
    ...    before that is over. So the keyword waits for the extension host first, which
    ...    comes up later. Then it waits until the extension host knows the extension:
    ...    that is what the window has taken in. If it does not, the keyword installs the
    ...    extension again and reloads the window, so that VS Code reads its extensions
    ...    anew. The script can also fail once because VS Code writes the list of
    ...    extensions at the same time, so the first install is tried twice.
    ...
    ...    `extension` is a Marketplace id or a `.vsix` file; for a `.vsix` file, give its
    ...    id as `id`.
    [Arguments]    ${extension}    ${id}=${extension}
    ${dirs} =    Get VS Code Instance Directories
    Evaluate In Extension Host    () => true
    Wait Until Keyword Succeeds    2x    1s
    ...    Execute VS Code CLI Command In Instance    ${dirs}    --install-extension    ${extension}
    ${known} =    Run Keyword And Return Status    Wait Until Keyword Succeeds    10s    0.2s
    ...    Extension Host Should Know    ${id}
    IF    not ${known}
        Run Keyword And Ignore Error    Execute VS Code CLI Command In Instance    ${dirs}    --uninstall-extension    ${id}
        Execute VS Code CLI Command In Instance    ${dirs}    --install-extension    ${extension}
        Evaluate In Extension Host
        ...    (vscode) => { void vscode.commands.executeCommand('workbench.action.reloadWindow'); }
        Wait Until Keyword Succeeds    30s    0.5s    Extension Host Should Know    ${id}
    END

Extension Host Should Know
    [Documentation]    Fails unless the extension host of the active window knows the extension with the given id.
    [Arguments]    ${id}
    ${known} =    Evaluate In Extension Host    (vscode, id) => vscode.extensions.getExtension(id) !== undefined
    ...    arg=${id}
    Should Be True    ${known}    The extension host does not know ${id}.

Execute VS Code CLI Command In Instance
    [Documentation]    Runs VS Code's command-line script on the directories of a running VS Code.
    [Arguments]    ${dirs}    @{args}
    Execute VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    @{args}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
