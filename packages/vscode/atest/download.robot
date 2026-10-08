*** Settings ***
Library     OperatingSystem
Resource    resources/vscode.resource


*** Test Cases ***
Download Returns An Existing Executable
    ${code} =    Download VS Code    ${VSCODE_VERSION}    cache_dir=${VSCODE_CACHE}
    File Should Exist    ${code}
