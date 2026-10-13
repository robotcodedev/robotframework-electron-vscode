*** Settings ***
Name                Close VS Code
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
Instance Ends
    Start Test VS Code
    ${instance} =    Newest Instance
    VS Code Instance Is Running    ${instance}
    Close VS Code
    VS Code Instance Has Exited    ${instance}
