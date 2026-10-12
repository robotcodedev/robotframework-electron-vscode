*** Settings ***
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


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
        ${_}    ${_}    ${page} =    Start Fixture App    --views
        Get Title    ==    Views
        Get Page Ids    ACTIVE    ACTIVE    ACTIVE    ==    ${page}[page_id]
        Close Browser    CURRENT
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
    [Teardown]    Run Keywords    Remove Environment Variable    ROBOT_ONLY_IN_RUN    AND    Close Browser    ALL

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
    [Teardown]    Run Keywords    Remove Environment Variable    ELECTRON_RUN_AS_NODE    AND    Close Browser    ALL

Return Value
    ${browser_id}    ${context_id}    ${page} =    Start Fixture App
    Get Browser Ids    ACTIVE    contains    ${browser_id}
    Get Context Ids    ACTIVE    ACTIVE    contains    ${context_id}
    Get Page Ids    ACTIVE    ACTIVE    ACTIVE    contains    ${page}[page_id]

Browser Catalog Names The Application Electron
    ${browser_id}    ${_}    ${_} =    Start Fixture App
    Get Browser Catalog    validate    [b["type"] for b in value if b["id"] == "${browser_id}"] == ["electron"]
