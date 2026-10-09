*** Settings ***
Documentation       Runs commands in the integrated terminal and reads their output.

Library             String
Library             VSCode
Resource            command_palette.resource


*** Variables ***
# The rows of the active terminal.
${TERMINAL_ROWS}        .terminal-wrapper.active .xterm-rows
# A row of the active terminal that contains a text; {text} is replaced by the text.
${TERMINAL_TEXT}        .terminal-wrapper.active .xterm-rows >> text={text}


*** Keywords ***
Run In Terminal
    [Documentation]    Opens a new terminal and runs the given command in it.
    [Arguments]    ${command}
    Run Command    Terminal: Create New Terminal
    Wait For Elements State    ${TERMINAL_ROWS}    visible
    Keyboard Input    type    ${command}
    Keyboard Key    press    Enter

Terminal Should Show
    [Documentation]    Waits until the active terminal shows the given text.
    [Arguments]    ${text}
    ${output} =    Format String    ${TERMINAL_TEXT}    text=${text}
    Wait For Elements State    ${output}    visible
