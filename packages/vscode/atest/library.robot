*** Settings ***
Resource    resources/vscode.resource


*** Test Cases ***
Browser And Electron Keywords Without Prefix
    Keyword Should Exist    Click
    Keyword Should Exist    New Electron Application
    Keyword Should Exist    Get Browser Ids
