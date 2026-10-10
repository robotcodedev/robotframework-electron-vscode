*** Settings ***
Name                Tracing
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


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
    ${_}    ${context}    ${_} =    Start Fixture App
    Close Electron Application
    File Should Not Be Empty    ${OUTPUT_DIR}/browser/traces/trace_${context}.zip

No Tracing By Default
    ${_}    ${context}    ${_} =    Start Fixture App
    Close Electron Application
    File Should Not Exist    ${OUTPUT_DIR}/browser/traces/trace_${context}.zip
