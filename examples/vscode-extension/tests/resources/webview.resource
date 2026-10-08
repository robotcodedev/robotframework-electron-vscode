*** Settings ***
Documentation       Acts inside the webviews of an extension.

Library             String
Library             VSCode


*** Variables ***
# The frames that hold an extension's webview; {extension_id} is replaced by the extension's id.
${WEBVIEW_FRAMES}       iframe.webview.ready[src*="extensionId={extension_id}"] >>> iframe#active-frame


*** Keywords ***
Enter Webview
    [Documentation]    Makes the following Browser keywords act inside the webview of the given extension.
    ...
    ...    Sets Browser's selector prefix to the webview's frames until `Leave Webview`
    ...    or the end of the test, and returns the previous prefix for `Leave Webview`.
    [Arguments]    ${extension_id}
    ${frames} =    Format String    ${WEBVIEW_FRAMES}    extension_id=${extension_id}
    ${previous} =    Set Selector Prefix    ${frames} >>>    scope=Test
    RETURN    ${previous}

Leave Webview
    [Documentation]    Makes the following Browser keywords act on the workbench again.
    [Arguments]    ${previous}
    Set Selector Prefix    ${previous}    scope=Test
