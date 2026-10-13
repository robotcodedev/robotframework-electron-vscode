*** Settings ***
Resource    resources/vscode.resource


*** Test Cases ***
Browser And Electron Keywords Without Prefix
    Keyword Should Exist    Click
    Keyword Should Exist    Start Electron Application
    Keyword Should Exist    Switch Electron Application
    Run Keyword And Expect Error    No keyword with name 'New Context' found.    Keyword Should Exist    New Context
