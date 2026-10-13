*** Settings ***
Name                Install Into A Running Instance
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
Extension In A Running Instance
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${OUTPUT_DIR}/test-extension.vsix
    ${before} =    List User Extensions
    Start Test VS Code With Helper
    Install Into Running Instance    ${vsix}    robot.test-extension
    # An open palette does not refresh, so the command is looked up in a fresh one.
    Wait Until Keyword Succeeds    20s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Only The Given Instance Gets The Extension
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${OUTPUT_DIR}/test-extension.vsix
    ${first}    ${_} =    Start Test VS Code
    ${first_instance} =    Newest Instance
    Start Test VS Code
    ${second_instance} =    Newest Instance
    Switch Electron Application    ${first}
    Execute VS Code CLI Command    --install-extension    ${vsix}
    ${installed} =    List Directories In Directory    ${first_instance}/extensions    robot.test-extension-*
    Length Should Be    ${installed}    1
    ${installed} =    List Directories In Directory    ${second_instance}/extensions    robot.test-extension-*
    Length Should Be    ${installed}    0
