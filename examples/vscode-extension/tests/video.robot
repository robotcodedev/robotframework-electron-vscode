*** Settings ***
Documentation       Records videos of VS Code while the tests demonstrate the extension
...                 and create a Python script in the explorer and run it.
...
...                 The videos have the size of the screen, which the display profiles set with
...                 SCREEN_SIZE, so that the maximised VS Code fills them. Presenter mode slows the
...                 steps down and highlights what they act on, Playwright shows each action in the
...                 video, and the log embeds the videos. Browser closes VS Code at the end of each
...                 test, which finishes the video; in presenter mode it waits five seconds before,
...                 so that the video shows the result.
...
...                 The Python test needs network access for the Marketplace; leave it out with
...                 `--exclude network`.

Library             String
Resource            resources/vscode.resource
Resource            resources/command_palette.resource
Resource            resources/quick_pick.resource
Resource            resources/notifications.resource
Resource            resources/webview.resource
Resource            resources/editor.resource
Resource            resources/explorer.resource
Resource            resources/python.resource
Resource            resources/terminal.resource

Suite Setup         Set Presenter Mode    ${{ {"duration": "1s"} }}
Suite Teardown      Set Presenter Mode    False


*** Test Cases ***
Demonstration Of The Extension
    Open Example VS Code With Video
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

Python Script Created And Run
    [Tags]    network
    Open Example VS Code With Video    extensions=${{ ["ms-python.python"] }}
    Create File In Explorer    greeting.py
    Active Editor Should Be    greeting.py
    Keyboard Input    type    print("Hello Robot Framework")
    Save File
    Run Python File
    Terminal Should Show    Hello Robot Framework


*** Keywords ***
Open Example VS Code With Video
    [Documentation]    Opens VS Code and records a video in the size of the screen.
    ...    Further named arguments, such as `extensions`, are passed on.
    [Arguments]    &{options}
    ${width}    ${height} =    Split String    %{SCREEN_SIZE=1920x1080}    x
    VAR    &{size}    width=${width}    height=${height}
    VAR    &{show_actions}    duration=${800}    position=top-right
    VAR    &{record_video}    size=${size}    showActions=${show_actions}
    Open Example VS Code    record_video=${record_video}    &{options}
