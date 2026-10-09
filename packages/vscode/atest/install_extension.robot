*** Settings ***
Name                Install VS Code Extension
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Extension In A Running Instance
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${OUTPUT_DIR}/test-extension.vsix
    ${before} =    List User Extensions
    Open Test VS Code
    Install VS Code Extension    ${vsix}
    # VS Code registers the extension shortly after the install, and an open palette does not refresh.
    Wait Until Keyword Succeeds    20s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Only The Given Instance Gets The Extension
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${OUTPUT_DIR}/test-extension.vsix
    ${first}    ${_}    ${_} =    Open Test VS Code
    ${first_instance} =    Newest Instance
    Open Test VS Code
    ${second_instance} =    Newest Instance
    Install VS Code Extension    ${vsix}    browser=${first}
    ${installed} =    List Directories In Directory    ${first_instance}/extensions    robot.test-extension-*
    Length Should Be    ${installed}    1
    ${installed} =    List Directories In Directory    ${second_instance}/extensions    robot.test-extension-*
    Length Should Be    ${installed}    0

