*** Settings ***
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Application Opens A Window
    Start Fixture App
    Get Title    ==    Electron Fixture

Browser Keywords Act On The First Window
    Start Fixture App
    Click    id=change
    Get Text    id=change    ==    Clicked

Browser Keywords Act On The First Window With Views
    [Documentation]    With --views, the window shows a <webview> and a WebContentsView, which are pages as well.
    ...    Playwright sees the pages in a varying order, so the test starts the application three times.
    FOR    ${start}    IN RANGE    3
        ${_}    ${page} =    Start Fixture App    --views
        Get Title    ==    Views
        Get Page Ids    ACTIVE    ACTIVE    ACTIVE    ==    ${page}[page_id]
        Close Electron Application
    END

Arguments And Environment
    Set Environment Variable    ROBOT_ONLY_IN_RUN    visible-to-the-run
    ${env} =    Evaluate
    ...    {k: v for k, v in os.environ.items() if k not in ("ROBOT_ONLY_IN_RUN", "ELECTRON_RUN_AS_NODE")} | {"ROBOT_TEST_VAR": "from-test"}
    ...    modules=os
    Start Fixture App    --flag-from-test    env=${env}    cwd=${TEMPDIR}
    Get Text    id=args    *=    --flag-from-test
    Get Text    id=cwd    ==    ${TEMPDIR}
    Get Text    id=test-var    ==    from-test
    Get Text    id=run-only-var    ==    ${EMPTY}
    [Teardown]    Run Keywords    Remove Environment Variable    ROBOT_ONLY_IN_RUN    AND    Close Electron Application    ALL

Default Working Directory
    Start Fixture App
    Get Text    id=cwd    ==    ${EXECDIR}

Relative Executable Path
    ${electron} =    Get Electron Executable    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}    ${ELECTRON_CACHE}
    ${relative} =    Evaluate    os.path.relpath(shutil.which($electron))    modules=os,shutil
    Should Not Be Equal    ${relative}    ${{ os.path.abspath($relative) }}
    ${app} =    Get Fixture App
    ${user_data} =    New User Data Dir    ${OUTPUT_DIR}
    New Electron Application    ${relative}    args=${{ [$app, "--user-data-dir=" + $user_data] }}
    Get Title    ==    Electron Fixture

Test Run Started From Inside VS Code
    Set Environment Variable    ELECTRON_RUN_AS_NODE    1
    Start Fixture App
    Get Text    id=run-as-node    ==    ${EMPTY}
    [Teardown]    Run Keywords    Remove Environment Variable    ELECTRON_RUN_AS_NODE    AND    Close Electron Application    ALL

Return Value
    ${app}    ${page} =    Start Fixture App
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$app] }}
    Get Page Ids    ACTIVE    ACTIVE    ACTIVE    ==    ${page}[page_id]
