*** Settings ***
Name                Download
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Download In An Application
    ${url} =    Web Server Url
    Start Fixture App
    Go To    ${url}
    ${download} =    Download    ${url}api    saveAs=${OUTPUT_DIR}/downloads/answer.json
    ${content} =    Get File    ${download}[saveAs]
    Should Be Equal    ${content}    {"answer": 42}
