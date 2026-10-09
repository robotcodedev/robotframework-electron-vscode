*** Settings ***
Documentation       Creates files in the explorer.

Library             VSCode


*** Variables ***
# The explorer's view of the workspace folder.
${EXPLORER}                 .explorer-folders-view
# The explorer's action that creates a file; it shows while the mouse is over the explorer.
${EXPLORER_NEW_FILE}        .pane-header [aria-label="New File..."]
# The input in which the explorer asks for the name of a new file.
${EXPLORER_NAME_INPUT}      .explorer-folders-view input[aria-label^="Type file name"]


*** Keywords ***
Create File In Explorer
    [Documentation]    Creates a file in the workspace folder with the explorer's *New File...* action.
    ...    VS Code opens the new file in the editor.
    [Arguments]    ${name}
    Hover    ${EXPLORER}
    Click    ${EXPLORER_NEW_FILE}
    Fill Text    ${EXPLORER_NAME_INPUT}    ${name}
    Keyboard Key    press    Enter
