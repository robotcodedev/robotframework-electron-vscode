*** Settings ***
Documentation       Runs commands through the command palette.

Library             String
Library             VSCode


*** Variables ***
# The palette row of a command; {title} is replaced by the command's title.
${COMMAND_PALETTE_ROW}      .quick-input-list .monaco-list-row[aria-label*="{title}"]


*** Keywords ***
Run Command
    [Documentation]    Runs the command with the given title, for example `Robot Example: Say Hello`.
    ...
    ...    The command palette filters asynchronously. The keyword waits for the
    ...    command's row before it presses Enter, so it never runs another command.
    [Arguments]    ${title}
    ${row} =    Format String    ${COMMAND_PALETTE_ROW}    title=${title}
    Keyboard Key    press    F1
    Keyboard Input    type    ${title}
    Wait For Elements State    ${row}    visible
    Keyboard Key    press    Enter
