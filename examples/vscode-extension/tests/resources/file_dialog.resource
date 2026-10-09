*** Settings ***
Documentation       Opens files through VS Code's own file dialog.
...
...                 VS Code shows native file dialogs, which Browser cannot reach. With the
...                 setting `files.simpleDialog.enable`, which `Open Example VS Code` sets, it shows
...                 its own dialog in the quick input instead.

Library             VSCode
Resource            command_palette.resource


*** Variables ***
# The path input of VS Code's own file dialog.
${FILE_DIALOG_INPUT}    .quick-input-widget .quick-input-box input
# The first entry of the folder that the dialog lists.
${FILE_DIALOG_ENTRY}    .quick-input-list .monaco-list-row >> nth=0


*** Keywords ***
Open File With Dialog
    [Documentation]    Opens the file with the given path through *File: Open File...*.
    [Arguments]    ${path}
    Run Command    File: Open File...
    # The dialog loads its folder asynchronously and then sets the input to it, so the
    # path is filled in only after the folder is listed, and checked before Enter.
    Wait For Elements State    ${FILE_DIALOG_ENTRY}    visible
    Fill Text    ${FILE_DIALOG_INPUT}    ${path}
    Get Property    ${FILE_DIALOG_INPUT}    value    ==    ${path}
    Keyboard Key    press    Enter
