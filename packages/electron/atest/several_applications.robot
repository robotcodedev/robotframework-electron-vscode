*** Settings ***
Resource            resources/fixture.resource

Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Switch Between Applications
    ${first}    ${_} =    Start Fixture App
    Start Fixture App    --page\=second.html
    Get Title    ==    Second Window
    ${previous} =    Switch Electron Application    ${first}
    Get Title    ==    Electron Fixture
    ${active} =    Get Electron Application Ids    ACTIVE
    Should Be Equal    ${active}    ${{ [$first] }}
    ${current} =    Get Electron Application Ids    CURRENT
    Should Be Equal    ${current}    ${{ [$first] }}
    ${ids} =    Get Electron Application Ids
    Should Be Equal    ${{ sorted($ids) }}    ${{ sorted([$first, $previous]) }}

Catalog Of The Applications
    ${app}    ${page_details} =    Start Fixture App
    Click    id=open
    Wait Until Keyword Succeeds    10s    200ms
    ...    Get Page Ids    ALL    ACTIVE    ACTIVE    validate    len(value) == 2
    ${catalog} =    Get Electron Application Catalog
    Should Be Equal    ${catalog}[0][id]    ${app}
    Should Be True    ${catalog}[0][active]
    VAR    @{titles}
    VAR    @{active}
    FOR    ${page}    IN    @{catalog}[0][pages]
        VAR    @{titles}    @{titles}    ${page}[title]
        IF    ${page}[active]    VAR    @{active}    @{active}    ${page}[id]
    END
    Should Be Equal    ${{ sorted($titles) }}    ${{ ["Electron Fixture", "Second Window"] }}
    Should Be Equal    ${active}    ${{ [$page_details["page_id"]] }}

Close All Applications
    Start Fixture App    --all-first
    Start Fixture App    --all-second
    Close Electron Application    ALL
    Fixture App Has Exited    --all-first
    Fixture App Has Exited    --all-second
    ${ids} =    Get Electron Application Ids
    Should Be Empty    ${ids}
