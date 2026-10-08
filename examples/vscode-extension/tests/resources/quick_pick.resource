*** Settings ***
Documentation       Selects items of quick picks that an extension shows.

Library             String
Library             VSCode


*** Variables ***
# The row of a quick pick item; {label} is replaced by the item's label.
${QUICK_PICK_ITEM}      .quick-input-list .monaco-list-row[aria-label*="{label}"]


*** Keywords ***
Select Quick Pick Item
    [Documentation]    Selects the item with the given label in the open quick pick.
    [Arguments]    ${label}
    ${item} =    Format String    ${QUICK_PICK_ITEM}    label=${label}
    Wait For Elements State    ${item}    visible
    Click    ${item}
