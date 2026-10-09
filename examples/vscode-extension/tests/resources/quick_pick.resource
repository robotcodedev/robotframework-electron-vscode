*** Settings ***
Documentation       Selects items of quick picks that an extension shows.

Library             String
Library             VSCode


*** Variables ***
# The row of exactly this quick pick item; {label} is replaced by the item's label. The row's
# aria-label is the label, or the label followed by ", " and the item's description.
${QUICK_PICK_ITEM}      .quick-input-list .monaco-list-row[aria-label="{label}"], .quick-input-list .monaco-list-row[aria-label^="{label}, "]


*** Keywords ***
Quick Pick Item Should Be Shown
    [Documentation]    Waits until the open quick pick shows the item with the given label.
    [Arguments]    ${label}
    ${item} =    Format String    ${QUICK_PICK_ITEM}    label=${label}
    Wait For Elements State    ${item}    visible

Select Quick Pick Item
    [Documentation]    Selects the item with the given label in the open quick pick.
    [Arguments]    ${label}
    Quick Pick Item Should Be Shown    ${label}
    ${item} =    Format String    ${QUICK_PICK_ITEM}    label=${label}
    Click    ${item}
