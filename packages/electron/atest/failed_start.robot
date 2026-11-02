*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Wrong Executable Path
    Run Keyword And Expect Error    *'/does/not/exist/electron' not found*
    ...    Start Electron Application    /does/not/exist/electron
    ${ids} =    Get Electron Application Ids
    Should Be Empty    ${ids}

No Window
    Run Keyword And Expect Error    *Timeout*
    ...    Start Fixture App    --no-window    timeout=2s
    ${ids} =    Get Electron Application Ids
    Should Be Empty    ${ids}
    ${processes} =    Count Fixture App Processes    --no-window
    Should Be Equal As Integers    ${processes}    0

Application Ends During The Start
    Start Fixture App
    # Python refuses Electron's arguments, prints its usage and ends at once.
    Run Keyword And Expect Error    *Process failed to launch*usage:*
    ...    Start Electron Application    ${{ sys.executable }}
    Open Application And Next Start Work

Application Does Not Answer In Time
    Start Fixture App
    Run Keyword And Expect Error    *Timeout 50ms exceeded*
    ...    Start Fixture App    --answers-too-late    timeout=50ms
    Wait Until Keyword Succeeds    10s    100ms    Fixture App Has Exited    --answers-too-late
    Open Application And Next Start Work


*** Keywords ***
Open Application And Next Start Work
    Get Title    ==    Electron Fixture
    ${ids} =    Get Electron Application Ids
    Length Should Be    ${ids}    1
    Start Fixture App
