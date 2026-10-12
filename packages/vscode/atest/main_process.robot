*** Settings ***
Name                Main Process
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
VS Code's Version From Its Main Process
    Open Test VS Code
    ${version} =    Evaluate In Main Process    ({ app }) => app.getVersion()
    # The profile vscode-insiders sets the version to "insiders", whose number changes with every build,
    # and a local VS Code from VSCODE_EXECUTABLE has its own version.
    IF    $VSCODE_EXECUTABLE is None and $VSCODE_VERSION[0].isdigit()
        Should Be Equal    ${version}    ${VSCODE_VERSION}
    ELSE
        Should Match Regexp    ${version}    ^\\d+\\.\\d+\\.\\d+
    END
