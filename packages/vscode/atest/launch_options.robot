*** Settings ***
Name                Launch Options
Resource            resources/vscode.resource

Test Teardown       Close Browser    ALL


*** Test Cases ***
Options Reach The Workbench
    Open Test VS Code    color_scheme=dark    locale=pt-BR    timezone_id=Asia/Tokyo
    ${workbench} =    Evaluate JavaScript    ${None}
    ...    () => ({
    ...        dark: matchMedia('(prefers-color-scheme: dark)').matches,
    ...        language: navigator.language,
    ...        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ...    })
    Should Be Equal    ${workbench}    ${{ {"dark": True, "language": "pt-BR", "timeZone": "Asia/Tokyo"} }}

Script Added To The Workbench
    Open Test VS Code    bypass_csp=True
    Evaluate JavaScript    ${None}
    ...    () => {
    ...        const script = document.createElement('script');
    ...        script.text = "document.body.dataset.robotScript = 'ran'";
    ...        document.head.append(script);
    ...    }
    Get Attribute    body    data-robot-script    ==    ran
