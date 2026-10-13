*** Settings ***
Documentation       Starts VS Code with the extension of this folder.

Library             OperatingSystem
Library             VSCode


*** Variables ***
# VSCODE_EXECUTABLE, the VS Code that the tests run against, comes from robot.toml or a personal .robot.toml.
# The library's helper extension for Evaluate In Extension Host, from the installed package.
${HELPER_EXTENSION}     ${{ pathlib.Path(VSCode.__file__).parent / 'extension' }}


*** Keywords ***
Start Example VS Code
    [Documentation]    Starts an isolated VS Code with the extension of this folder loaded from source,
    ...    next to the library's helper extension for `Evaluate In Extension Host`.
    ...
    ...    VS Code opens a fresh copy of `tests/workspace`, see `Example Workspace`, so
    ...    that tests can change files. It opens maximised, so that it fills the screen;
    ...    on Xvfb and Xephyr this needs a window manager, which the display profiles
    ...    start. Its own file dialog replaces the native one, which Browser cannot reach,
    ...    and its terminal runs `sh`, independent of personal shell configuration.
    ...    Named arguments of `Start VS Code`, such as `extensions_dir` or `record_video`, are
    ...    passed on.
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
    VAR    @{development}    ${EXECDIR}    ${HELPER_EXTENSION}
    Start VS Code    ${VSCODE_EXECUTABLE}    ${workspace}
    ...    extension_development_path=${development}
    ...    settings=${settings}
    ...    &{options}

Example Workspace
    [Documentation]    Returns the folder of the workspace copy that `Start Example VS Code` opens in this suite.
    RETURN    ${OUTPUT_DIR}/workspaces/${SUITE NAME}
