*** Settings ***
Documentation       Opens and saves files in the editor.

Library             String
Library             VSCode


*** Variables ***
# The Quick Open row of a file; {name} is replaced by the file name.
${QUICK_OPEN_ROW}       .quick-input-list .monaco-list-row[aria-label^="{name}, "]
# The active editor tab of a file; {name} is replaced by the file name.
${ACTIVE_TAB}           .tabs-container .tab.active[aria-label="{name}"]


*** Keywords ***
Open File
    [Documentation]    Opens a file of the workspace through Quick Open, for example `notes.txt`.
    [Arguments]    ${name}
    ${row} =    Format String    ${QUICK_OPEN_ROW}    name=${name}
    Keyboard Key    press    ControlOrMeta+p
    Keyboard Input    type    ${name}
    Wait For Elements State    ${row}    visible
    Keyboard Key    press    Enter
    Active Editor Should Be    ${name}

Active Editor Should Be
    [Documentation]    Waits until the file with the given name is open in the active editor.
    [Arguments]    ${name}
    ${tab} =    Format String    ${ACTIVE_TAB}    name=${name}
    Wait For Elements State    ${tab}    visible

Save File
    [Documentation]    Saves the file in the active editor.
    Keyboard Key    press    ControlOrMeta+s
