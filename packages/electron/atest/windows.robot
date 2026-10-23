*** Settings ***
Library             String
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

Windows Of An Application
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    ${windows} =    Get Window Ids
    Length Should Be    ${windows}    2
    Should Match Regexp    ${windows}[1]    ^window=\\d+$

Views Are Not Windows
    Start Fixture App    --views
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    ${windows} =    Get Window Ids
    Length Should Be    ${windows}    1

Window Of The Active View
    Start Fixture App    --views
    ${window} =    Get Window Ids    ACTIVE
    ${view} =    Page Id With Title    View
    Switch Page    ${view}
    ${active} =    Get Window Ids    ACTIVE
    Should Be Equal    ${active}    ${window}

Active Page And Focus Unchanged
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    # Waits until the window shows the title of its page instead of the application's name.
    Get Window State    window=title=Second Window
    Focused Window Should Be    Second Window
    Get Window Ids
    Get Title    ==    Second Window
    Focused Window Should Be    Second Window

Window Titles
    Start Fixture App
    Click    id=open
    # Waits until the window shows the title of its page instead of the application's name.
    Get Window State    window=title=Second Window
    ${titles} =    Get Window Titles
    Should Be Equal    ${titles}    ${{ ["Electron Fixture", "Second Window"] }}

Title Set By The Application
    Start Fixture App
    Evaluate In Main Process    (electron, arg, window) => {
    ...        window.on('page-title-updated', (event) => event.preventDefault());
    ...        window.setTitle('Native Title');
    ...    }
    ${titles} =    Get Window Titles
    Should Be Equal    ${titles}    ${{ ["Native Title"] }}
    Get Title    ==    Electron Fixture

Window That Opens Later
    Start Fixture App
    Click    id=open
    Maximize Window    title=Second Window
    Get Window State    ==    maximized    window=title=Second Window

Id As A Named Argument
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    ${windows} =    Get Window Ids
    ${number} =    Remove String    ${windows}[1]    window=
    Maximize Window    window=${number}
    Get Window State    ==    maximized    window=${windows}[1]

Two Windows With One Title
    Set Browser Timeout    1s    scope=Test
    Start Fixture App    --views
    Open Window With Views
    Run Keyword And Expect Error    *2 windows show the title 'Views'*
    ...    Maximize Window    title=Views

Unknown Id
    Start Fixture App
    Run Keyword And Expect Error    *The application has no window 'window=99'.*
    ...    Get Window State    window=window=99

Maximise The Window Of The Active View
    Start Fixture App    --views
    ${window} =    Get Window Ids    ACTIVE
    ${view} =    Page Id With Title    View
    Switch Page    ${view}
    Maximize Window
    Get Window State    ==    maximized    window=${window}[0]

Maximise Another Window
    Start Fixture App
    Click    id=open
    Get Window State    window=title=Second Window
    ${windows} =    Get Window Ids
    Maximize Window    ${windows}[1]
    Get Window State    ==    maximized    window=${windows}[1]
    Get Window State    ==    normal
    Get Title    ==    Electron Fixture

Size Of A Window
    Start Fixture App
    Set Window Size    1024    700
    ${size} =    Evaluate JavaScript    ${None}    () => [window.innerWidth, window.innerHeight]
    Should Be Equal    ${size}    ${{ [1024, 700] }}

Size Of A Maximised Window
    Start Fixture App
    Maximize Window
    Set Window Size    1024    700
    Get Window State    ==    normal
    Get Window Size    ALL    ==    {'width': 1024, 'height': 700}

Size After Setting It
    Start Fixture App
    Set Window Size    1024    700
    ${size} =    Get Window Size
    Should Be Equal    ${size}    ${{ {"width": 1024, "height": 700} }}
    Get Window Size    width    ==    1024

Failing Assertion
    Start Fixture App
    Run Keyword And Expect Error    Window width is*
    ...    Get Window Size    width    ==    1

Maximise
    Start Fixture App
    ${before} =    Get Window Size    width
    Maximize Window
    Get Window State    ==    maximized
    Get Window Size    width    >    ${before}

Minimise And Restore
    Start Fixture App
    ${before} =    Get Window Size
    Minimize Window
    Get Window State    ==    minimized
    Restore Window
    Get Window State    ==    normal
    Get Window Size    ALL    ==    ${before}

Restore A Maximised Window
    Start Fixture App
    ${before} =    Get Window Size
    Maximize Window
    Restore Window
    Get Window State    ==    normal
    Get Window Size    ALL    ==    ${before}

Restore A Window That Was Maximised Before It Was Minimised
    Start Fixture App
    Maximize Window
    Minimize Window
    Restore Window
    Get Window State    ==    normal

Restore A Fullscreen Window
    Start Fixture App
    Evaluate In Main Process    (electron, arg, window) => window.setFullScreen(true)
    Get Window State    ==    maximized
    Restore Window
    Get Window State    ==    normal
    ${fullscreen} =    Evaluate In Main Process    (electron, arg, window) => window.isFullScreen()
    Should Not Be True    ${fullscreen}

Fullscreen Window
    Start Fixture App
    Evaluate In Main Process    (electron, arg, window) => window.setFullScreen(true)
    Get Window State    ==    maximized

Started Application
    Start Fixture App
    Get Window State    ==    normal

No Application Open
    Run Keyword And Expect Error    No application is open.    Maximize Window

Window With A Webview
    [Documentation]    The fixture's views page opens a second window that shows a <webview> as well.
    Start Fixture App    --views
    Click    id=open
    Get Window State    window=title=Webview Window
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 5
    ${titles} =    Get Window Titles
    Should Be Equal    ${titles}    ${{ ["Views", "Webview Window"] }}

Switch By Title And Back
    Start Fixture App
    Click    id=open
    ${previous} =    Switch Window    title=Second Window
    Get Title    ==    Second Window
    Switch Window    ${previous}
    Get Title    ==    Electron Fixture

Switch By Window Id
    Start Fixture App
    Click    id=open
    Get Window State    window=title=Second Window
    ${windows} =    Get Window Ids
    Switch Window    ${windows}[1]
    Get Title    ==    Second Window

Window Whose Webview Loads Later
    Start Fixture App    --views
    Click    id=open
    Switch Window    title=Webview Window
    Get Title    ==    Webview Window
    Get Url    *=    webview-window.html

Title Set By The Application For Switching
    Start Fixture App
    Click    id=open
    Get Window State    window=title=Second Window
    Evaluate In Main Process    ({ BrowserWindow }) => {
    ...        const second = BrowserWindow.getAllWindows().find((window) => window.getTitle() === 'Second Window');
    ...        second.on('page-title-updated', (event) => event.preventDefault());
    ...        second.setTitle('Native Title');
    ...        return second.webContents.executeJavaScript("document.title = 'Page Title'");
    ...    }
    Switch Window    title=Native Title
    Get Title    ==    Page Title

Pages With One Title
    Set Browser Timeout    1s    scope=Test
    Start Fixture App    --views
    Open Window With Views
    ${windows} =    Get Window Ids
    Run Keyword And Expect Error    *all have the title 'Views'*
    ...    Switch Window    ${windows}[1]
    ${active} =    Get Window Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$windows[0]] }}

Page Id Of A Window
    ${_}    ${page} =    Start Fixture App
    Click    id=open
    Switch Window    title=Second Window
    Switch Window    ${page}[page_id]
    Get Title    ==    Electron Fixture

Page Of A View
    Start Fixture App    --views
    ${view} =    Page Id With Title    View
    Run Keyword And Expect Error    *The page '${view}' is not a window*
    ...    Switch Window    ${view}
    Get Title    ==    Views

Page Of Another Application
    ${first}    ${page} =    Start Fixture App
    Start Fixture App    --page\=second.html
    Switch Window    ${page}[page_id]
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$first] }}
    Get Title    ==    Electron Fixture

Window Opened By A Click
    Start Fixture App
    Click    id=open
    Switch Window    new
    Get Title    ==    Second Window

View Newer Than The New Window
    Start Fixture App    --views
    Click    id=open
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 5
    Run Keyword And Expect Error    *The newest page is not a window*
    ...    Switch Window    NEW
    Get Title    ==    Views

No New Page
    Set Browser Timeout    1s    scope=Test
    Start Fixture App
    Run Keyword And Expect Error    *no new pages*
    ...    Switch Window    NEW
    Get Title    ==    Electron Fixture

Title As A Regular Expression
    Start Fixture App
    Click    id=open
    Maximize Window    title=/^second WINDOW$/i
    Get Window State    ==    maximized    window=title=Second Window

Expression That Matches Two Windows
    Set Browser Timeout    1s    scope=Test
    Start Fixture App
    Click    id=open
    Get Window State    window=title=Second Window
    Run Keyword And Expect Error    *2 windows show a title that matches /o/*
    ...    Maximize Window    title=/o/

Switch By A Regular Expression
    Start Fixture App
    Click    id=open
    Switch Window    title=/^Second/
    Get Title    ==    Second Window

Page Without A Title
    Set Browser Timeout    1s    scope=Test
    Start Fixture App
    Evaluate In Main Process    ({ BrowserWindow, app }) => {
    ...        const window = new BrowserWindow({ width: 600, height: 400 });
    ...        return window.loadFile(app.getAppPath() + '/untitled.html');
    ...    }
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 2
    ${windows} =    Get Window Ids
    Run Keyword And Expect Error    *has no title*
    ...    Switch Window    ${windows}[1]
    Get Title    ==    Electron Fixture


*** Keywords ***
Open Window With Views
    [Documentation]    Opens a second window with the page of the first one, so that both show the title "Views".
    Evaluate In Main Process    ({ BrowserWindow }, url) => {
    ...        const window = new BrowserWindow({ width: 600, height: 400, webPreferences: { webviewTag: true } });
    ...        return window.loadURL(url);
    ...    }
    ...    arg=${{ __import__("pathlib").Path($EXECDIR, "packages/electron/atest/fixtures/app/views.html").as_uri() }}
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 5
    # A window shows the application's name until it takes over the title of its page.
    Wait Until Keyword Succeeds    10s    100ms    Window Titles Should Be    Views    Views

Window Titles Should Be
    [Arguments]    @{titles}
    ${actual} =    Get Window Titles
    Should Be Equal    ${actual}    ${titles}

Page Id With Title
    [Documentation]    The id of the active application's page with the title, from the catalog.
    [Arguments]    ${title}
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    ${catalog} =    Get Electron Application Catalog
    VAR    ${pages}    ${catalog}[0][pages]
    FOR    ${page}    IN    @{pages}
        IF    $page["title"] == $title    RETURN    ${page}[id]
    END
    Fail    No page with the title '${title}'.

Focused Window Should Be
    [Arguments]    ${title}
    ${focused} =    Evaluate In Main Process    ({ BrowserWindow }) => BrowserWindow.getFocusedWindow()?.getTitle()
    Should Be Equal    ${focused}    ${title}
