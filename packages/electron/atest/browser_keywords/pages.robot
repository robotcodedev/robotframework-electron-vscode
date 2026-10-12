*** Settings ***
Documentation       The windows, webviews and views of an application as Browser pages.
Resource            ../resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Second Window
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    Get Title    ==    Second Window
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 2

Webview And View By Page Id
    Start Fixture App    --views
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    ${catalog} =    Get Electron Application Catalog
    ${titles} =    Evaluate    sorted(page["title"] for page in $catalog[0]["pages"])
    Should Be Equal    ${titles}    ${{ ["Guest", "View", "Views"] }}
    Switch To Page With Title    Guest
    Get Text    id=guest-text    ==    Inside the webview
    Switch To Page With Title    View
    Get Text    id=view-text    ==    Inside the view

Close Page On A View
    Start Fixture App    --views
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    Switch To Page With Title    View
    Close Page
    ${catalog} =    Get Electron Application Catalog
    ${titles} =    Evaluate    sorted(page["title"] for page in $catalog[0]["pages"])
    Should Be Equal    ${titles}    ${{ ["Guest", "Views"] }}
    ${views} =    Evaluate In Main Process
    ...    ({ BrowserWindow }) => BrowserWindow.getAllWindows()[0].contentView.children.length
    Should Be Equal    ${views}    ${0}

Webview Removed From Its Page
    [Documentation]    Close Page waits forever on a <webview>, so a test removes the element from its page instead.
    Start Fixture App    --views
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    Switch To Page With Title    Views
    Evaluate JavaScript    id=guest    (element) => element.remove()
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 2

Frame Selector Does Not Reach Into A Webview
    Start Fixture App    --views
    Wait For Elements State    id=guest    attached
    Run Keyword And Expect Error    *<iframe> was expected*    Get Element Count    id=guest >>> id=guest-text

Window Closed By The Application
    Start Fixture App
    Click    id=open
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 2
    Evaluate In Main Process
    ...    ({ BrowserWindow }) => BrowserWindow.getAllWindows().find((w) => w.getTitle() === 'Second Window').close()
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 1
    ${ids} =    Get Page Ids    ALL    ACTIVE    ACTIVE
    Switch Page    ${ids}[0]
    Get Title    ==    Electron Fixture

Application That Quits By Itself
    ${app}    ${_} =    Start Fixture App    --quits-by-itself
    Evaluate In Main Process    ({ app }) => { setTimeout(() => app.quit(), 100); }
    Wait Until Keyword Succeeds    10s    200ms    Fixture App Has Exited    --quits-by-itself
    ${ids} =    Get Electron Application Ids
    Should Contain    ${ids}    ${app}
    Run Keyword And Expect Error    *No page open*    Get Title
    Close Electron Application    ${app}
    ${ids} =    Get Electron Application Ids
    Should Not Contain    ${ids}    ${app}

Last Window Closed With Close Page
    Start Fixture App    --last-window
    Close Page
    Wait Until Keyword Succeeds    10s    200ms    Fixture App Has Exited    --last-window


*** Keywords ***
Switch To Page With Title
    [Arguments]    ${title}
    ${ids} =    Get Page Ids    ALL    ACTIVE    ACTIVE
    FOR    ${id}    IN    @{ids}
        Switch Page    ${id}
        ${page_title} =    Get Title
        IF    $page_title == $title    RETURN
    END
    Fail    No page with the title '${title}'.
