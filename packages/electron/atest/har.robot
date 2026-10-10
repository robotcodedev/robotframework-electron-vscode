*** Settings ***
Name                HAR
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
HAR Of An Application
    ${url} =    Web Server Url
    Start Fixture App    record_har=${{ {"path": "har/application.har"} }}
    Go To    ${url}
    Click    id=load
    Get Text    id=result    ==    {"answer": 42}
    Close Electron Application
    ${har} =    Get File    ${OUTPUT_DIR}/har/application.har
    Should Contain    ${har}    ${url}api
    Should Contain    ${har}    {\\"answer\\": 42}
