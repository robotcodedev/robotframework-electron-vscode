*** Settings ***
Name                Main Process
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
VS Code's Version From Its Main Process
    Start Test VS Code
    ${version} =    Evaluate In Main Process    ({ app }) => app.getVersion()
    Should Be The Version Of The Executable    ${version}
