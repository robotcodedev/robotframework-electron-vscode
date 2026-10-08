*** Settings ***
Library     Electron
Library     Electron.Helper
Library     ElectronFixture.py


*** Variables ***
${ELECTRON_VERSION}         44.7.0
${ELECTRON_EXECUTABLE}      ${NONE}
${ELECTRON_CACHE}           ${CURDIR}/../../../../.cache/electron


*** Keywords ***
Start Fixture App
    [Arguments]    @{extra_args}    &{options}
    ${electron} =    Get Electron Executable    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}    ${ELECTRON_CACHE}
    ${app} =    Get Fixture App
    ${ids} =    New Electron Application    ${electron}    args=${{ [$app, *$extra_args] }}    &{options}
    RETURN    ${ids}

Fixture App Is Running
    [Arguments]    ${marker}
    ${processes} =    Count Fixture App Processes    ${marker}
    Should Be True    ${processes} > 0

Fixture App Has Exited
    [Arguments]    ${marker}
    ${processes} =    Count Fixture App Processes    ${marker}
    Should Be Equal As Integers    ${processes}    0
