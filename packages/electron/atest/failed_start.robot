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
