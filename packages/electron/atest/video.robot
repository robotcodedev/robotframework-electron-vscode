*** Settings ***
Name                Video
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Video Of An Application
    ${_}    ${_}    ${page} =    Start Fixture App    record_video=${{ {} }}
    Should Start With    ${page}[video_path]    ${OUTPUT_DIR}${/}browser${/}video${/}
    Click    id=change
    Get Text    id=change    ==    Clicked
    Close Electron Application
    File Should Not Be Empty    ${page}[video_path]

Action Overlay
    VAR    &{show_actions}    duration=${500}    position=top-right
    ${_}    ${_}    ${page} =    Start Fixture App    record_video=${{ {"showActions": $show_actions} }}
    Click    id=change
    Close Electron Application
    File Should Not Be Empty    ${page}[video_path]

No Recording By Default
    ${_}    ${_}    ${page} =    Start Fixture App
    Should Be Empty    ${page}[video_path]
