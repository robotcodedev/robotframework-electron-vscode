*** Settings ***
Name                Launch Options
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Variables ***
${ADD_SCRIPT}       () => {
...                     const script = document.createElement('script');
...                     script.text = "document.getElementById('result').textContent = 'Script ran'";
...                     document.head.append(script);
...                 }


*** Test Cases ***
Application Decides The Color Scheme
    Start Fixture App    --dark
    ${dark} =    Evaluate JavaScript    ${None}    () => matchMedia('(prefers-color-scheme: dark)').matches
    Should Be True    ${dark}

Emulated Color Scheme
    Start Fixture App    --dark    color_scheme=light
    ${light} =    Evaluate JavaScript    ${None}    () => matchMedia('(prefers-color-scheme: light)').matches
    Should Be True    ${light}

Given Locale And Time Zone
    Start Fixture App    locale=pt-BR    timezone_id=Asia/Tokyo
    ${formats} =    Evaluate JavaScript    ${None}
    ...    () => ({
    ...        language: navigator.language,
    ...        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ...        number: (1234.5).toLocaleString(),
    ...    })
    Should Be Equal    ${formats}    ${{ {"language": "pt-BR", "timeZone": "Asia/Tokyo", "number": "1.234,5"} }}

Script Added To A Page With A Strict Policy
    Start Fixture App    --page\=csp.html    bypass_csp=True
    Evaluate JavaScript    ${None}    ${ADD_SCRIPT}
    Get Text    id=result    ==    Script ran

Bypassed Policy With Views
    [Documentation]    The fixture's views page has a <webview> and a WebContentsView, which load again as well.
    Start Fixture App    --views    bypass_csp=True
    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 3
    ${windows} =    Get Window Ids
    Length Should Be    ${windows}    1

Bypassed Policy With A Window That Closes During The Start
    [Documentation]    The fixture's first window closes when it loads again and leaves another window behind.
    Start Fixture App    --close-on-reload    bypass_csp=True
    Switch Window    title=Second Window
    Get Title    ==    Second Window

Policy Enforced By Default
    Start Fixture App    --page\=csp.html
    Run Keyword And Expect Error    *TrustedScript*    Evaluate JavaScript    ${None}    ${ADD_SCRIPT}
    Get Text    id=result    ==    ${EMPTY}
