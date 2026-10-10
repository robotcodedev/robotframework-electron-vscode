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
