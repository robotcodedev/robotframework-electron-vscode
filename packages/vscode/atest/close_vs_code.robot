*** Settings ***
Name                Close VS Code
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Instance Ends
    Open Test VS Code
    ${instance} =    Newest Instance
    VS Code Instance Is Running    ${instance}
    Close VS Code
    VS Code Instance Has Exited    ${instance}
