*** Settings ***
Name        Helper
Library     OperatingSystem
Library     VSCode.Helper
Resource    resources/variables.resource


*** Test Cases ***
Executable From The Helper
    ${code} =    Get VS Code Executable    ${VSCODE_VERSION}    ${VSCODE_EXECUTABLE}    ${VSCODE_CACHE}
    File Should Exist    ${code}
