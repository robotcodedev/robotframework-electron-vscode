*** Settings ***
Name                Start VS Code
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close VS Code    ALL


*** Test Cases ***
Workbench Is Ready
    Start Test VS Code
    Get Element States    .monaco-workbench    contains    visible

Executable Behind A Symbolic Link
    VAR    ${link}    ${OUTPUT_DIR}/links/code
    Remove Directory    ${OUTPUT_DIR}/links    recursive=True
    Create Directory    ${OUTPUT_DIR}/links
    Evaluate    os.symlink(os.path.abspath($VSCODE_EXECUTABLE), $link)    modules=os
    Start VS Code    ${link}
    Get Element States    .monaco-workbench    contains    visible
    # Without the link, the upload of the results on CI does not take the VS Code that it points to.
    [Teardown]    Run Keywords    Close VS Code    ALL    AND    Remove Directory    ${OUTPUT_DIR}/links    recursive=True

Executable Is Required
    Run Keyword And Expect Error    *expected 1 to 2 *arguments, got 0*
    ...    Start VS Code    # robotcode: ignore[DataError]
    ${ids} =    Get Electron Application Ids
    Should Be Empty    ${ids}

Prepared Extensions Directory
    VAR    ${prepared}    ${OUTPUT_DIR}/prepared
    Remove Directory    ${prepared}    recursive=True
    ${vsix} =    Pack Extension    ${TEST_EXTENSION}    ${prepared}/test-extension.vsix
    Execute VS Code CLI Command    --install-extension    ${vsix}
    ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${prepared}/extensions
    Copy Directory    ${prepared}/extensions    ${prepared}/copy
    Start Test VS Code    extensions_dir=${prepared}/copy
    Wait Until Keyword Succeeds    20s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot

Development Extension Is Active
    Start Test VS Code    extension_development_path=${TEST_EXTENSION}
    # VS Code registers the commands of the development extension shortly after the start, and an open palette does not refresh.
    Wait Until Keyword Succeeds    30s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot

Folder
    Start Test VS Code    ${TEST_WORKSPACE}
    Get Title    *=    workspace

Trace And HAR Of The Workbench
    Start Test VS Code
    ...    tracing=${OUTPUT_DIR}/traces/workbench.zip    record_har=${{ {"path": "har/workbench.har"} }}
    Get Element States    .monaco-workbench    contains    visible
    Close VS Code
    File Should Not Be Empty    ${OUTPUT_DIR}/traces/workbench.zip
    File Should Not Be Empty    ${OUTPUT_DIR}/har/workbench.har

Video Of The Workbench
    ${_}    ${page} =    Start Test VS Code
    ...    extension_development_path=${TEST_EXTENSION}    record_video=${{ {"size": {"width": 1280, "height": 800}} }}
    Should Start With    ${page}[video_path]    ${OUTPUT_DIR}${/}browser${/}video${/}
    Set Viewport Size    1280    800
    # VS Code registers the commands of the development extension shortly after the start, and an open palette does not refresh.
    Wait Until Keyword Succeeds    30s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    Close VS Code
    File Should Not Be Empty    ${page}[video_path]
