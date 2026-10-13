*** Settings ***
Name                Main Process
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Value From The Main Process
    Start Fixture App
    ${name} =    Evaluate In Main Process    ({ app }) => app.getName()
    Should Be Equal    ${name}    robotframework-electron-fixture

Native Dialog Replaced
    Start Fixture App
    Evaluate In Main Process    ({ dialog }, path) => {
    ...        dialog.showOpenDialog = async () => ({ canceled: false, filePaths: [path] });
    ...    }
    ...    arg=/data/report.csv
    Click    id=open-file
    Get Text    id=opened    ==    /data/report.csv

Not An Electron Application
    Start Fixture App
    Run Keyword And Expect Error
    ...    *Browser 'browser=unknown' is not an application started by 'Start Electron Application'.
    ...    Evaluate In Main Process    () => 1    application=browser=unknown

No Application Open
    Run Keyword And Expect Error    No application is open.    Evaluate In Main Process    () => 1

Window Sized From The Main Process
    Start Fixture App
    Evaluate In Main Process    (electron, size, window) => window.setBounds(size)
    ...    arg=${{ {"width": 1024, "height": 700} }}
    ${size} =    Evaluate JavaScript    ${None}    () => ({ width: window.outerWidth, height: window.outerHeight })
    Should Be Equal    ${size}    ${{ {"width": 1024, "height": 700} }}

Window Of The Active Page
    Start Fixture App
    Click    id=open
    Switch Page    NEW
    ${title} =    Evaluate In Main Process    (electron, arg, window) => window.getTitle()
    Should Be Equal    ${title}    Second Window

Active Page Of Another Browser
    ${app}    ${_} =    Start Fixture App
    Start Fixture App    --page\=second.html
    ${no_window} =    Evaluate In Main Process    (electron, arg, window) => window === null    application=${app}
    Should Be True    ${no_window}
