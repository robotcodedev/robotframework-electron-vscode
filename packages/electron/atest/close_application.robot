*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Close The Active Application
    New Browser    chromium    headless=True
    ${web_browser} =    Get Browser Ids    ACTIVE
    Start Fixture App    --close-active
    Close Electron Application
    Fixture App Has Exited    --close-active
    Get Browser Ids    ACTIVE    ==    @{web_browser}

Close By Browser Id
    ${first}    ${_}    ${_} =    Start Fixture App    --close-by-id-first
    ${second}    ${_}    ${_} =    Start Fixture App    --close-by-id-second
    Close Electron Application    ${first}
    Fixture App Has Exited    --close-by-id-first
    Get Browser Ids    ACTIVE    contains    ${second}

Application Already Exited
    Start Fixture App    --already-exited
    Close Page
    Wait Until Keyword Succeeds    10s    200ms    Fixture App Has Exited    --already-exited
    Close Electron Application

