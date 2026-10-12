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

Policy Enforced By Default
    Start Fixture App    --page\=csp.html
    Run Keyword And Expect Error    *TrustedScript*    Evaluate JavaScript    ${None}    ${ADD_SCRIPT}
    Get Text    id=result    ==    ${EMPTY}
