*** Settings ***
Documentation       Checks the notifications that VS Code shows.

Library             String
Library             VSCode


*** Variables ***
# A notification toast with the given text; {message} is replaced by the text.
${NOTIFICATION}     .notifications-toasts .notification-list-item-message >> text="{message}"


*** Keywords ***
Notification Should Be Shown
    [Documentation]    Waits until a notification with exactly the given text is shown.
    [Arguments]    ${message}
    ${notification} =    Format String    ${NOTIFICATION}    message=${message}
    Wait For Elements State    ${notification}    visible
