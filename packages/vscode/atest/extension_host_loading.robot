*** Settings ***
Name                Loading The Helper Extension
Documentation       The library does not load its helper extension: a test loads its folder as a development
...                 extension, or installs its .vsix. Without the helper, or with one of another version,
...                 Evaluate In Extension Host fails. The library's timeout is short, for the failures.
Library             OperatingSystem
Resource            resources/vscode.resource

Suite Setup         Set Browser Timeout    5s
Test Teardown       Close VS Code    ALL


*** Test Cases ***
Installed From The VSIX
    File Should Exist    ${HELPER_VSIX}
    ...    The helper's .vsix is missing. Build it with 'uv build --package robotframework-vscode'.
    VAR    ${prepared}    ${OUTPUT_DIR}/installed-helper
    Remove Directory    ${prepared}    recursive=True
    Execute VS Code CLI Command    --install-extension    ${HELPER_VSIX}
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${prepared}/extensions
    Start Test VS Code    extensions_dir=${prepared}/extensions
    Get Title    not contains    [Extension Development Host]
    ${version} =    Evaluate In Extension Host    (vscode) => vscode.version
    Should Match Regexp    ${version}    ^\\d+\\.\\d+\\.\\d+

VS Code Without The Helper
    Start Test VS Code
    Get Title    not contains    [Extension Development Host]
    Run Keyword And Expect Error
    ...    GLOB:No extension host of the VS Code instance answered within 5 seconds. The library's helper extension may not be loaded: give its folder '${HELPER_EXTENSION}' to Start VS Code in extension_development_path, or install '${HELPER_VSIX}' *
    ...    Evaluate In Extension Host    () => 1

Helper Of Another Version
    ${helper} =    Copy Helper With Version    ${OUTPUT_DIR}/helper-0.0.1    0.0.1
    Start Test VS Code    extension_development_path=${helper}
    VAR    ${marker}    ${OUTPUT_DIR}/function-ran
    Remove File    ${marker}
    Run Keyword And Expect Error
    ...    GLOB:The helper extension in this VS Code has the version 0.0.1, but the library has *. Install '${HELPER_VSIX}' of this version *
    ...    Evaluate In Extension Host
    ...    (vscode, path) => vscode.workspace.fs.writeFile(vscode.Uri.file(path), new Uint8Array())    arg=${marker}
    File Should Not Exist    ${marker}

Only The Given Development Extensions
    Start Test VS Code    ${TEST_WORKSPACE}    extension_development_path=${TEST_EXTENSION}
    ${arguments} =    Evaluate In Main Process    () => process.argv
    ${paths} =    Evaluate    [arg for arg in $arguments if arg.startswith("--extensionDevelopmentPath=")]
    Should Be Equal    ${paths}    ${{ ["--extensionDevelopmentPath=" + $TEST_EXTENSION] }}
