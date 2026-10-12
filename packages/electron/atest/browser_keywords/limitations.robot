*** Settings ***
Documentation       Browser keywords that the library hides, and visible keywords that fail on an application, with
...                 the errors that the guide on Browser keywords quotes. When the test of a failing keyword fails
...                 after an upgrade of Browser or Playwright, the keyword may work now: update the guide and turn the
...                 test into one that uses the keyword.
Resource            ../resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Hidden Keywords
    [Documentation]    Keywords for browsers and contexts, and keywords that cannot work on an application.
    [Template]    Keyword Should Be Hidden
    New Browser
    Open Browser
    Close Browser
    Switch Browser
    Get Browser Ids
    Get Browser Catalog
    Launch Browser Server
    Close Browser Server
    Connect To Browser
    New Context
    New Persistent Context
    Close Context
    Switch Context
    Get Context Ids
    New Page
    Get Device
    Get Devices
    Crawl Site
    Set Storage State
    Tap
    Save Page As Pdf

Save Storage State With An Origin That Is No Longer Open
    [Documentation]    Playwright opens a page of its own to read the local storage of an origin that no window shows.
    Start Fixture App    --page\=keywords.html
    ${url} =    Web Server Url
    Go To    ${url}
    ${app} =    Get Fixture App
    Go To    file://${app}/keywords.html
    Run Keyword And Expect Error    *Target.createTarget*Not supported*    Save Storage State


*** Keywords ***
Keyword Should Be Hidden
    [Arguments]    ${name}
    Run Keyword And Expect Error    No keyword with name '${name}' found.    Keyword Should Exist    ${name}
