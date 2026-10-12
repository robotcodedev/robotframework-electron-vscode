*** Settings ***
Name                Tracing
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Trace Of An Application
    Start Fixture App    tracing=${OUTPUT_DIR}/traces/application.zip
    Click    id=change
    Get Text    id=change    ==    Clicked
    Close Electron Application
    ${trace} =    Read Trace    ${OUTPUT_DIR}/traces/application.zip
    Should Contain    ${trace}[actions]    click
    Should Contain    ${trace}[groups]    Electron.Click

Tracing From The Global Setting
    VAR    ${ROBOT_FRAMEWORK_BROWSER_TRACING}    True    scope=TEST
    ${before} =    Trace Files
    Start Fixture App
    Close Electron Application
    ${after} =    Trace Files
    Length Should Be    ${{ set($after) - set($before) }}    1

No Tracing By Default
    ${before} =    Trace Files
    Start Fixture App
    Close Electron Application
    ${after} =    Trace Files
    Should Be Equal    ${after}    ${before}


*** Keywords ***
Trace Files
    [Documentation]    The traces in Browser's trace folder. With tracing=True, Browser names them after the context.
    Create Directory    ${OUTPUT_DIR}/browser/traces
    ${files} =    List Files In Directory    ${OUTPUT_DIR}/browser/traces    trace_*.zip
    RETURN    ${files}
