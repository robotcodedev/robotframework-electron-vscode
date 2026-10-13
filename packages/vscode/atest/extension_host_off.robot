*** Settings ***
Name                Extension Host Switched Off
Documentation       With enable_extension_host_evaluation=False, Open VS Code leaves the library's helper
...                 extension out. The suite imports the library itself, with its own import arguments.
Library             VSCode    enable_extension_host_evaluation=False    timeout=5s
Resource            resources/variables.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
Helper Switched Off
    Open VS Code    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
    Get Title    not contains    [Extension Development Host]
    Run Keyword And Expect Error    *import argument enable_extension_host_evaluation=False switches off.
    ...    Evaluate In Extension Host    () => 1

Browser's Import Arguments
    ${previous} =    Set Browser Timeout    10s    scope=Test
    Should Be Equal    ${previous}    5 seconds
    Open VS Code    ${TEST_WORKSPACE}
    ...    version=${VSCODE_VERSION}    executable=${VSCODE_EXECUTABLE}    cache_dir=${VSCODE_CACHE}
    ...    extension_development_path=${TEST_EXTENSION}
    ${arguments} =    Evaluate In Main Process    () => process.argv
    ${paths} =    Evaluate    [arg for arg in $arguments if arg.startswith("--extensionDevelopmentPath=")]
    Should Be Equal    ${paths}    ${{ ["--extensionDevelopmentPath=" + $TEST_EXTENSION] }}
