*** Settings ***
Documentation       Cookies, storage, emulation and the clock of an application's context.
Library             OperatingSystem
Resource            ../resources/fixture.resource

Suite Setup         Start Fixture App    --page\=keywords.html
Suite Teardown      Close Electron Application    ALL


*** Test Cases ***
Cookies
    ${url} =    Web Server Url
    Go To    ${url}
    Add Cookie    flavour    chocolate    url=${url}
    ${cookie} =    Get Cookie    flavour
    Should Be Equal    ${cookie.value}    chocolate
    ${cookies} =    Get Cookies
    Length Should Be    ${cookies}    1
    Delete All Cookies
    ${cookies} =    Get Cookies
    Should Be Empty    ${cookies}

Storage
    Go To Keywords Page
    LocalStorage Set Item    colour    blue
    LocalStorage Get Item    colour    ==    blue
    SessionStorage Set Item    size    large
    SessionStorage Get Item    size    ==    large
    LocalStorage Set Item    shape    round
    LocalStorage Remove Item    colour
    LocalStorage Get Item    colour    ==    ${None}
    LocalStorage Get Item    shape    ==    round
    LocalStorage Clear
    LocalStorage Get Item    shape    ==    ${None}
    SessionStorage Remove Item    size
    SessionStorage Get Item    size    ==    ${None}
    SessionStorage Set Item    weight    heavy
    SessionStorage Clear
    SessionStorage Get Item    weight    ==    ${None}

Saved Storage State
    [Documentation]    Playwright saves the storage of the http and https origins the context has visited. Each of
    ...    them must still be open in a window: for any other, it opens a page of its own, which Electron does
    ...    not allow. The local storage of file:// pages is not saved.
    ${url} =    Web Server Url
    Go To    ${url}
    LocalStorage Set Item    colour    blue
    ${state} =    Save Storage State
    ${saved} =    Get File    ${state}
    Should Contain    ${saved}    "value": "blue"

Emulation
    ${url} =    Web Server Url
    Go To    ${url}
    ${size} =    Get Viewport Size
    Should Be Equal    ${size}    ${None}
    Set Viewport Size    640    480
    Get Viewport Size    width    ==    640
    ${width} =    Evaluate JavaScript    ${None}    () => window.innerWidth
    Should Be Equal    ${width}    ${640}
    Emulate Media    colorScheme=dark    reducedMotion=reduce
    ${media} =    Evaluate JavaScript    ${None}
    ...    () => [matchMedia('(prefers-color-scheme: dark)').matches, matchMedia('(prefers-reduced-motion: reduce)').matches]
    Should Be Equal    ${media}    ${{ [True, True] }}
    Grant Permissions    geolocation
    Set Geolocation    60.17    24.94
    ${position} =    Evaluate JavaScript    ${None}
    ...    () => new Promise((resolve, reject) => navigator.geolocation.getCurrentPosition(
    ...        (position) => resolve([position.coords.latitude, position.coords.longitude]), reject))
    Should Be Equal    ${position}    ${{ [60.17, 24.94] }}
    Clear Permissions
    Set Offline    True
    ${online} =    Evaluate JavaScript    ${None}    () => navigator.onLine
    Should Not Be True    ${online}
    Set Offline    False

Clock
    Go To Keywords Page
    Set Time    2026-01-01 12:00:00
    ${year} =    Evaluate JavaScript    ${None}    () => new Date().getFullYear()
    Should Be Equal    ${year}    ${2026}
    Pause At    2026-01-01 13:00:00
    Advance Clock    1 hour
    ${hour} =    Evaluate JavaScript    ${None}    () => new Date().getHours()
    Should Be Equal    ${hour}    ${14}
    Resume Clock


*** Keywords ***
Go To Keywords Page
    ${app} =    Get Fixture App
    Go To    file://${app}/keywords.html
