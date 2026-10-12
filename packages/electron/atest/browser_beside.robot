*** Settings ***
Documentation       A web browser beside an application needs the Browser library as well. Keywords that both
...                 libraries have need the library name as prefix.
Library             Browser
Resource            resources/fixture.resource

Test Teardown       Run Keywords    Browser.Close Browser    ALL    AND    Close Electron Application    ALL


*** Test Cases ***
Web Page Beside An Application
    Start Fixture App
    ${app} =    Get Fixture App
    Browser.New Browser    chromium    headless=True
    Browser.New Page    file://${app}/second.html
    Browser.Get Title    ==    Second Window
    Electron.Get Title    ==    Electron Fixture
