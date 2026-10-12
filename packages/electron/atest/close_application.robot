*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Close The Active Application
    ${before}    ${_} =    Start Fixture App    --previously-active
    Start Fixture App    --close-active
    Close Electron Application
    Fixture App Has Exited    --close-active
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$before] }}

Close By Browser Id
    ${first}    ${_} =    Start Fixture App    --close-by-id-first
    ${second}    ${_} =    Start Fixture App    --close-by-id-second
    Close Electron Application    ${first}
    Fixture App Has Exited    --close-by-id-first
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$second] }}

Application Already Exited
    Start Fixture App    --already-exited
    Close Page
    Wait Until Keyword Succeeds    10s    200ms    Fixture App Has Exited    --already-exited
    Close Electron Application
