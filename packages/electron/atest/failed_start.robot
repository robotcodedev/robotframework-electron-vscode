*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Wrong Executable Path
    Run Keyword And Expect Error    *'/does/not/exist/electron' not found*
    ...    New Electron Application    /does/not/exist/electron
    Get Browser Ids    ALL    validate    len(value) == 0

No Window
    Run Keyword And Expect Error    *Timeout*
    ...    Start Fixture App    --no-window    timeout=2s
    Get Browser Ids    ALL    validate    len(value) == 0
    ${processes} =    Count Fixture App Processes    --no-window
    Should Be Equal As Integers    ${processes}    0
