*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


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
