*** Settings ***
Documentation       Browser's selectors in a window of an application.
Resource            ../resources/fixture.resource

Suite Setup         Start Fixture App    --page\=keywords.html
Suite Teardown      Close Electron Application    ALL


*** Test Cases ***
Selector Strategies
    Get Text    css=#locate-me    ==    Locate me
    Get Text    button#locate-me    ==    Locate me
    Get Text    xpath=//button[@id="locate-me"]    ==    Locate me
    Get Text    //button[@id="locate-me"]    ==    Locate me
    Get Text    text=Locate me    ==    Locate me
    Get Text    "Locate me"    ==    Locate me
    Get Text    text=/locate me/i    ==    Locate me
    Get Text    id=locate-me    ==    Locate me
    Get Text    data-testid=by-testid    ==    Locate me
    Get Text    data-test-id=by-test-id    ==    Locate me
    Get Text    data-test=by-test    ==    Locate me
    Get Text    role=button[name="Locate me"]    ==    Locate me

Get Element By
    ${label} =    Get Element By    Label    Name
    Get Attribute    ${label}    id    ==    name
    ${placeholder} =    Get Element By    Placeholder    Your name
    Get Attribute    ${placeholder}    id    ==    name
    ${title} =    Get Element By    Title    Paragraph title
    Get Attribute    ${title}    id    ==    text
    ${alt} =    Get Element By    AltText    Fixture logo
    Get Attribute    ${alt}    id    ==    logo
    ${test_id} =    Get Element By    TestId    by-testid
    Get Text    ${test_id}    ==    Locate me
    ${text} =    Get Element By    Text    Locate me    exact=True
    Get Attribute    ${text}    id    ==    locate-me
    ${role} =    Get Element By Role    button    name=Locate me
    Get Attribute    ${role}    id    ==    locate-me

Combined Selectors
    Get Text    section[aria-label="Locators"] >> button    ==    Locate me
    Get Text    section[aria-label="Form"] >> button >> nth=0    ==    Clicks: 0
    Get Element Count    button >> visible=true    >    5
    Get Text    button:has-text("Locate")    ==    Locate me
    Get Text    section:has(#name) >> button    ==    Locate me
    Get Text    button:text-is("Locate me")    ==    Locate me
    ${section} =    Get Element    section[aria-label="Locators"]
    Get Text    ${section} >> button    ==    Locate me

Shadow DOM
    Get Text    css=#in-shadow    ==    Inside the shadow root
    Get Text    id=in-shadow    ==    Inside the shadow root
    Get Text    text=Inside the shadow root    ==    Inside the shadow root
    Get Element Count    css:light=#in-shadow    ==    0
    Get Element Count    id:light=in-shadow    ==    0
    Get Element Count    text:light=Inside the shadow root    ==    0
    Get Element Count    xpath=//span[@id="in-shadow"]    ==    0

Frames
    Get Text    id=frame >>> id=in-frame    ==    In the frame

Strict Mode And Selector Prefix
    Run Keyword And Expect Error    *strict mode violation*    Get Text    button
    Set Selector Prefix    section[aria-label="Locators"] >>    scope=Test
    Get Text    button    ==    Locate me

ARIA References
    ${snapshot} =    Get Aria Snapshot    section[aria-label="Locators"]    mode=ai
    ${ref} =    Evaluate    re.search(r'button "Locate me" \\[ref=(\\w+)\\]', $snapshot).group(1)    modules=re
    Get Text    aria-ref=${ref}    ==    Locate me

React And Vue Selectors Fail
    [Documentation]    Playwright 1.63 still lists ``_react=`` and ``_vue=``, but they fail. When this test fails after
    ...    an upgrade, the selectors work again: update the guide on Browser keywords.
    Run Keyword And Expect Error    *Cannot read properties of undefined*    Get Element Count    _react=Button
    Run Keyword And Expect Error    *Cannot read properties of undefined*    Get Element Count    _vue=button

Custom Selector Engine
    [Documentation]    An engine applies to pages that load after it is registered, so the window loads again.
    Register Tag Selector Engine
    Reload
    Get Text    tag=h1    ==    Keywords
