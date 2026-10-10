*** Settings ***
Name                Open VS Code
Library             OperatingSystem
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Workbench Is Ready
    Open Test VS Code
    Get Element States    .monaco-workbench    contains    visible

Local Installation
    ${code} =    Get VS Code Executable    ${VSCODE_VERSION}    cache_dir=${VSCODE_CACHE}
    Open VS Code    executable=${code}    cache_dir=${TEMPDIR}/vscode-never-downloaded
    Get Element States    .monaco-workbench    contains    visible
    Directory Should Not Exist    ${TEMPDIR}/vscode-never-downloaded

Development Extension Is Active
    Open Test VS Code    extension_development_path=${TEST_EXTENSION}
    # VS Code registers the commands of the development extension shortly after the start, and an open palette does not refresh.
    Wait Until Keyword Succeeds    30s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot

Folder
    Open Test VS Code    ${TEST_WORKSPACE}
    Get Title    *=    workspace

Trace And HAR Of The Workbench
    Open Test VS Code
    ...    tracing=${OUTPUT_DIR}/traces/workbench.zip    record_har=${{ {"path": "har/workbench.har"} }}
    Get Element States    .monaco-workbench    contains    visible
    Close VS Code
    File Should Not Be Empty    ${OUTPUT_DIR}/traces/workbench.zip
    File Should Not Be Empty    ${OUTPUT_DIR}/har/workbench.har

Video Of The Workbench
    ${_}    ${_}    ${page} =    Open Test VS Code
    ...    extension_development_path=${TEST_EXTENSION}    record_video=${{ {"size": {"width": 1280, "height": 800}} }}
    Should Start With    ${page}[video_path]    ${OUTPUT_DIR}${/}browser${/}video${/}
    Set Viewport Size    1280    800
    # VS Code registers the commands of the development extension shortly after the start, and an open palette does not refresh.
    Wait Until Keyword Succeeds    30s    1s    Run Command From A Fresh Palette    Robot Test: Say Hello
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    Close VS Code
    File Should Not Be Empty    ${page}[video_path]
