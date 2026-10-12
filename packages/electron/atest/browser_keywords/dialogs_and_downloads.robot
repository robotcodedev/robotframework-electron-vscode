*** Settings ***
Documentation       Dialogs and downloads in a window of an application. Each test starts the application, because a
...                 dialog handler stays on its page, and Handle Future Dialogs and Wait For Alert on the same page
...                 crash Browser's Node process.
Library             OperatingSystem
Resource            ../resources/fixture.resource

Test Setup          Start Fixture App    --page\=keywords.html
Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Handle Future Dialogs
    Handle Future Dialogs    accept
    Click    id=alert
    Get Text    id=dialog-result    ==    Alerted
    Handle Future Dialogs    accept
    Click    id=confirm
    Get Text    id=dialog-result    ==    Confirmed
    Handle Future Dialogs    dismiss
    Click    id=confirm
    Get Text    id=dialog-result    ==    Dismissed

Dialogs Without A Handler Are Dismissed
    Click    id=confirm
    Get Text    id=dialog-result    ==    Dismissed

Wait For Alerts
    ${promise} =    Promise To    Wait For Alert    accept    text=Hello from the fixture
    Click    id=alert
    ${message} =    Wait For    ${promise}
    Should Be Equal    ${message}    Hello from the fixture
    ${promise} =    Promise To    Wait For Alerts    ["accept", "dismiss"]    [None, None]    [None, None]
    Click    id=alert
    Click    id=confirm
    Wait For    ${promise}
    Get Text    id=dialog-result    ==    Dismissed

Download After A Click
    ${promise} =    Promise To Wait For Download    saveAs=${OUTPUT_DIR}/downloads/hello.txt
    Click    id=download
    ${download} =    Wait For    ${promise}
    ${content} =    Get File    ${download}[saveAs]
    Should Be Equal    ${content}    Hello from the fixture

Download State
    ${promise} =    Promise To Wait For Download    wait_for_finished=False
    Click    id=download
    ${download} =    Wait For    ${promise}
    Get Download State    ${download}    validate    value["state"] in ("inProgress", "finished")

Cancel Download
    ${url} =    Web Server Url
    Go To    ${url}
    ${promise} =    Promise To Wait For Download    wait_for_finished=False
    Click    id=slow
    ${download} =    Wait For    ${promise}
    Get Download State    ${download}    validate    value["state"] == "in_progress"
    Cancel Download    ${download}
    Get Download State    ${download}    validate    value["state"] == "canceled"
