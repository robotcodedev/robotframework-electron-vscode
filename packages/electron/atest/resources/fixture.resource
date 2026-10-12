*** Settings ***
Library     Electron
Library     Electron.Helper
Library     ElectronFixture.py
Resource    variables.resource



*** Keywords ***
Start Fixture App
    [Arguments]    @{extra_args}    &{options}
    ${electron} =    Get Electron Executable    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}    ${ELECTRON_CACHE}
    ${app} =    Get Fixture App
    ${user_data} =    New User Data Dir    ${OUTPUT_DIR}
    ${ids} =    New Electron Application    ${electron}
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
