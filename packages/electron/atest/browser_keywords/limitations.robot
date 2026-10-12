*** Settings ***
Documentation       Browser keywords that fail on an application, with the errors that the guide on Browser keywords
...                 quotes. When a test fails after an upgrade of Browser or Playwright, its keyword may work now:
...                 update the guide and turn the test into one that uses the keyword.
Library             OperatingSystem
Resource            ../resources/fixture.resource

Test Setup          Start Fixture App    --page\=keywords.html
Test Teardown       Close Browser    ALL


*** Test Cases ***
New Page
    [Documentation]    The application creates its windows, and Electron does not let Playwright open one.
    Run Keyword And Expect Error    *Target.createTarget*Not supported*    New Page    about:blank

New Context
    [Documentation]    The application's context is its only one. Browser has no browser object to create another.
    Run Keyword And Expect Error    *Trying to create a new context when a persistentContext is active*
    ...    New Context

Crawl Site
    [Documentation]    It opens pages of its own, as New Page does.
    ${app} =    Get Fixture App
    Run Keyword And Expect Error    *Target.createTarget*Not supported*    Crawl Site    file://${app}/keywords.html

Set Storage State
    [Documentation]    Playwright opens a page of its own to write the local storage of an origin.
    ${state} =    Set Variable
    ...    {"cookies": [], "origins": [{"origin": "http://127.0.0.1:1", "localStorage": [{"name": "colour", "value": "blue"}]}]}
    Create File    ${OUTPUT_DIR}/storage/state.json    ${state}
    Run Keyword And Expect Error    *Target.createTarget*Not supported*
    ...    Set Storage State    ${OUTPUT_DIR}/storage/state.json

Save Storage State With An Origin That Is No Longer Open
    [Documentation]    Playwright opens a page of its own to read the local storage of an origin that no window shows.
    ${url} =    Web Server Url
    Go To    ${url}
    ${app} =    Get Fixture App
    Go To    file://${app}/keywords.html
    Run Keyword And Expect Error    *Target.createTarget*Not supported*    Save Storage State

Tap
    [Documentation]    Touch needs the context option hasTouch, which Playwright's Electron launch does not have.
    Run Keyword And Expect Error    *does not support tap*    Tap    id=locate-me

Save Page As Pdf
    [Documentation]    Electron does not provide Chromium's PDF printing over the DevTools protocol.
    Run Keyword And Expect Error    *Page.printToPDF*    Save Page As Pdf    ${OUTPUT_DIR}/page.pdf
