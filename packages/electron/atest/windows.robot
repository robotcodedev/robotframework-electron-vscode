*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Second Window
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    Get Title    ==    Second Window

Closing A Window
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    Close Page
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 1
    Get Title    ==    Electron Fixture

Application And Web Browser
    ${app_browser_id}    ${_}    ${_} =    Start Fixture App
    New Browser    chromium    headless=True
    ${app} =    Get Fixture App
    New Page    file://${app}/second.html
    Get Title    ==    Second Window
    Switch Browser    ${app_browser_id}
    Get Title    ==    Electron Fixture
