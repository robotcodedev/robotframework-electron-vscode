*** Settings ***
Library     Electron
Library     ElectronFixture.py



*** Keywords ***
Start Fixture App
    [Arguments]    @{extra_args}    &{options}
    ${app} =    Get Fixture App
    ${user_data} =    New User Data Dir    ${OUTPUT_DIR}
    ${ids} =    Start Electron Application    ${ELECTRON_EXECUTABLE}
    ...    args=${{ [$app, "--user-data-dir=" + $user_data, *$extra_args] }}    &{options}
    RETURN    ${ids}

Fixture App Is Running
    [Arguments]    ${marker}
    ${processes} =    Count Fixture App Processes    ${marker}
    Should Be True    ${processes} > 0

Fixture App Has Exited
    [Arguments]    ${marker}
    ${processes} =    Count Fixture App Processes    ${marker}
    Should Be Equal As Integers    ${processes}    0
