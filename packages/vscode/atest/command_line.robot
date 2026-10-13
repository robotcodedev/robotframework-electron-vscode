*** Settings ***
Name                Command Line
Documentation       Execute VS Code CLI Command runs VS Code's command-line script on the active instance, or with
...                 an executable on the environment that Start VS Code gets with the same arguments.
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Variables ***
${PREPARED}     ${OUTPUT_DIR}/command-line


*** Test Cases ***
Extensions Of The Running Instance
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${PREPARED}/test-extension.vsix
    Remove Directory    ${PREPARED}/running    recursive=True
    Execute VS Code CLI Command    --install-extension    ${vsix}
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${PREPARED}/running/extensions
    Start Test VS Code    extensions_dir=${PREPARED}/running/extensions
    ${list} =    Execute VS Code CLI Command    --list-extensions
    Should Contain    ${list}    robot.test-extension

No Instance Open
    Run Keyword And Expect Error
    ...    ValueError: No VS Code instance is open. Give 'executable' to run the script without an instance.
    ...    Execute VS Code CLI Command    --list-extensions

Install Into A Prepared Directory
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${PREPARED}/test-extension.vsix
    Remove Directory    ${PREPARED}/prepared    recursive=True
    ${before} =    List User Extensions
    Execute VS Code CLI Command    --install-extension    ${vsix}
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${PREPARED}/prepared/extensions
    Start VS Code    ${VSCODE_EXECUTABLE}    extensions_dir=${PREPARED}/prepared/extensions
    # An open palette does not refresh, so the command is looked up in a fresh one.
    Wait Until Keyword Succeeds    20s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    ${after} =    List User Extensions
    Should Be Equal    ${before}    ${after}

Directories Without An Executable
    Run Keyword And Expect Error    ValueError: 'user_data_dir' and 'extensions_dir' need 'executable'.*
    ...    Execute VS Code CLI Command    --list-extensions    extensions_dir=${PREPARED}/extensions

Unknown Extension
    Run Keyword And Expect Error    VS Code's command line failed: *Extension 'robot.does-not-exist' not found*
    ...    Execute VS Code CLI Command    --install-extension    robot.does-not-exist    executable=${VSCODE_EXECUTABLE}

Empty Argument
    Run Keyword And Expect Error    ValueError: Argument 2 of the script is empty.*
    ...    Execute VS Code CLI Command    --install-extension    ${EMPTY}    executable=${VSCODE_EXECUTABLE}

No Arguments For The Script
    Run Keyword And Expect Error    ValueError: Execute VS Code CLI Command needs the script's arguments*
    ...    Execute VS Code CLI Command    executable=${VSCODE_EXECUTABLE}

No Window On Linux
    Skip If    not sys.platform.startswith('linux')    Only on Linux the script runs without a display.
    # Without a command, the script starts VS Code's window instead, which cannot open without a display.
    Execute VS Code CLI Command    --disable-extensions    executable=${VSCODE_EXECUTABLE}
    ${call} =    Newest Instance
    Sleep    3s    The window's process would show up within this time.
    ${processes} =    Count Processes With    ${call}${/}user-data
    Should Be Equal As Integers    ${processes}    0
