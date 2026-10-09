*** Settings ***
Documentation       Records a video of VS Code while the test demonstrates the extension.
...
...                 The video has the size of the screen, which the display profiles set with SCREEN_SIZE,
...                 so that the maximised VS Code fills it. Presenter mode slows the steps down and
...                 highlights what they act on, and Playwright shows each action in the video.

Library             OperatingSystem
Library             String
Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/quick_pick.resource
Resource            resources/notifications.resource
Resource            resources/webview.resource

Test Teardown       Set Presenter Mode    False


*** Test Cases ***
Demonstration Of The Extension
    ${_}    ${_}    ${page} =    Open Example VS Code With Video
    Set Presenter Mode    ${{ {"duration": "1s"} }}
    Run Command    Robot Example: Say Hello
    Notification Should Be Shown    Hello Robot
    Run Command    Robot Example: Pick
    Select Quick Pick Item    Banana
    Notification Should Be Shown    You picked Banana
    Run Command    Robot Example: Open Webview
    ${previous} =    Enter Webview    robot.example-extension
    Click    id=click-me
    Get Text    id=status    ==    Clicked
    Leave Webview    ${previous}
    Close VS Code
    # Playwright finishes the video when VS Code has closed.
    File Should Not Be Empty    ${page}[video_path]


*** Keywords ***
Open Example VS Code With Video
    [Documentation]    Opens VS Code and records a video in the size of the screen.
    ${width}    ${height} =    Split String    %{SCREEN_SIZE=1920x1080}    x
    VAR    &{size}    width=${width}    height=${height}
    VAR    &{show_actions}    duration=${800}    position=top-right
    VAR    &{record_video}    size=${size}    showActions=${show_actions}
    ${ids} =    Open Example VS Code    record_video=${record_video}
    RETURN    ${ids}
