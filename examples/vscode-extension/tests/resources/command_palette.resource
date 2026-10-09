*** Settings ***
Documentation       Runs commands through the command palette.

Library             String
Library             VSCode


*** Variables ***
# The palette row of exactly this command; {title} is replaced by the command's title. The row's
# aria-label is the title, or the title followed by ", " and its key binding or other hints.
${COMMAND_PALETTE_ROW}      .quick-input-list .monaco-list-row[aria-label="{title}"], .quick-input-list .monaco-list-row[aria-label^="{title}, "]
# How long to wait for a command that VS Code or an extension registers only after the start.
${COMMAND_TIMEOUT}          30s


*** Keywords ***
Run Command
    [Documentation]    Runs the command with the given title, for example `Robot Example: Say Hello`.
    ...
    ...    The command palette filters asynchronously. The keyword waits for the
    ...    command's row before it presses Enter, so it never runs another command.
    ...    Some commands are registered only a while after VS Code has started, or after
    ...    an extension has been installed, and an open palette does not show them.
    ...    The keyword therefore opens the palette again until the command is there,
    ...    without Browser's failure screenshots for the attempts in between.
    [Arguments]    ${title}
    ${row} =    Format String    ${COMMAND_PALETTE_ROW}    title=${title}
    ${on_failure} =    Register Keyword To Run On Failure    ${None}
    TRY
        Wait Until Keyword Succeeds    ${COMMAND_TIMEOUT}    1s    Find Command In A Fresh Palette    ${title}    ${row}
    FINALLY
        Register Keyword To Run On Failure    ${on_failure}
    END
    Keyboard Key    press    Enter

Find Command In A Fresh Palette
    [Documentation]    Opens the command palette, types the title and waits shortly for the command's row.
    [Arguments]    ${title}    ${row}
    Keyboard Key    press    Escape
    Keyboard Key    press    F1
    Keyboard Input    type    ${title}
    Wait For Elements State    ${row}    visible    timeout=2s
