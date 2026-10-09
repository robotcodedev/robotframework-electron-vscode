*** Settings ***
Documentation       Opens VS Code with the extension of this folder.

Library             OperatingSystem
Library             VSCode


*** Variables ***
# The VS Code version that the tests run against: a fixed version, `stable` or `insiders`.
${VSCODE_VERSION}       1.141.0
# An installed VS Code to use instead of a download, for example /usr/share/code/code.
${VSCODE_EXECUTABLE}    ${NONE}
# Where downloaded VS Code builds are cached; ${NONE} is the user's cache directory.
${VSCODE_CACHE}         ${NONE}


*** Keywords ***
Open Example VS Code
    [Documentation]    Opens an isolated VS Code with the extension of this folder loaded from source.
    ...
    ...    VS Code opens a fresh copy of `tests/workspace`, see `Example Workspace`, so
    ...    that tests can change files. It opens maximised, so that it fills the screen;
    ...    on Xvfb and Xephyr this needs a window manager, which the display profiles
    ...    start. Its own file dialog replaces the native one, which Browser cannot reach,
    ...    and its terminal runs `sh`, independent of personal shell configuration.
    ...    Named arguments of `Open VS Code`, such as `extensions`, are passed on.
    [Arguments]    &{options}
    ${workspace} =    Example Workspace
    Remove Directory    ${workspace}    recursive=True
    Copy Directory    ${EXECDIR}/tests/workspace    ${workspace}
    VAR    &{sh}    path=sh
    VAR    &{terminal_profiles}    sh=${sh}
    VAR    &{settings}
    ...    window.newWindowDimensions=maximized
    ...    files.simpleDialog.enable=${True}
    ...    terminal.integrated.profiles.linux=${terminal_profiles}
    ...    terminal.integrated.profiles.osx=${terminal_profiles}
    ...    terminal.integrated.defaultProfile.linux=sh
    ...    terminal.integrated.defaultProfile.osx=sh
    Open VS Code    ${workspace}
    ...    version=${VSCODE_VERSION}
    ...    executable=${VSCODE_EXECUTABLE}
    ...    cache_dir=${VSCODE_CACHE}
    ...    extension_development_path=${EXECDIR}
    ...    settings=${settings}
    ...    &{options}

Example Workspace
    [Documentation]    Returns the folder of the workspace copy that `Open Example VS Code` opens in this suite.
    RETURN    ${OUTPUT_DIR}/workspaces/${SUITE NAME}
