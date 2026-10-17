*** Settings ***
Name                Video
Library             OperatingSystem
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Video Of An Application
    ${_}    ${page} =    Start Fixture App    record_video=${{ {} }}
    Should Start With    ${page}[video_path]    ${OUTPUT_DIR}${/}browser${/}video${/}
    Click    id=change
    Get Text    id=change    ==    Clicked
    Close Electron Application
    File Should Not Be Empty    ${page}[video_path]

Action Overlay
    VAR    &{style}    title=font-size: 20px
    VAR    &{show_actions}    duration=${500}    position=top-right    style=${style}
    ${_}    ${page} =    Start Fixture App    record_video=${{ {"showActions": $show_actions} }}
    Click    id=change
    Close Electron Application
    File Should Not Be Empty    ${page}[video_path]

No Recording By Default
    ${_}    ${page} =    Start Fixture App
    Should Be Empty    ${page}[video_path]
