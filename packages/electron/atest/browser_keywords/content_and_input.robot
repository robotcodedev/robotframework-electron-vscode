*** Settings ***
Documentation       Reading content, input, screenshots and coverage in a window of an application.
Library             OperatingSystem
Resource            ../resources/fixture.resource

Suite Setup         Start Fixture App    --page\=keywords.html
Suite Teardown      Close Electron Application    ALL
Test Setup          Reload


*** Variables ***
${SECRET}       not in the log


*** Test Cases ***
Page Content
    Get Title    ==    Keywords
    Get Url    *=    keywords.html
    Get Page Source    *=    <h1 id="heading"
    Get Text    id=text    ==    Some bold text.
    Get Aria Snapshot    id=heading    yaml    *=    heading "Keywords"
    ${sum} =    Evaluate JavaScript    ${None}    () => 20 + 22
    Should Be Equal    ${sum}    ${42}

Element Details
    Get Attribute    id=text    title    ==    Paragraph title
    Get Attribute Names    id=heading    contains    class
    Get Property    id=name    placeholder    ==    Your name
    Get Style    id=heading    color    ==    rgb(0, 0, 255)
    Get Classes    id=heading    ==    title    main
    # 120px and two 1px borders. A fractional display scale snaps the borders to whole device pixels,
    # for example to 0.8px each at 125 %.
    Get BoundingBox    id=hover-target    width    validate    abs(value - 122) < 1
    Get Client Size    id=scroller    height    ==    80
    Get Scroll Size    id=scroller    height    ==    400
    Get Element Count    css=#table tr    ==    3
    Get Element States    id=name    contains    visible    editable

Table
    Get Table Cell Index    id=table >> "1.63"    ==    1
    Get Table Row Index    id=table >> "Playwright"    ==    2
    ${cell} =    Get Table Cell Element    id=table    "Version"    "Playwright"
    Get Text    ${cell}    ==    1.63

Form Input
    Fill Text    id=name    Robot
    Get Property    id=name    value    ==    Robot
    Type Text    id=notes    Typed    clear=True
    Get Property    id=notes    value    ==    Typed
    Clear Text    id=notes
    Get Property    id=notes    value    ==    ${EMPTY}
    Fill Secret    id=secret    $SECRET
    Get Property    id=secret    value    ==    ${SECRET}
    Check Checkbox    id=agree
    Get Checkbox State    id=agree    ==    checked
    Uncheck Checkbox    id=agree
    Get Checkbox State    id=agree    ==    unchecked
    Select Options By    id=color    value    green
    Get Selected Options    id=color    value    ==    green
    Get Select Options    id=sizes    validate    len(value) == 3
    Select Options By    id=sizes    text    S    L
    Deselect Options    id=sizes
    Get Selected Options    id=sizes    text    validate    value == []

File Upload
    Create File    ${OUTPUT_DIR}/upload/report.txt    report
    Upload File By Selector    id=upload    ${OUTPUT_DIR}/upload/report.txt
    Get Text    id=uploaded    ==    report.txt
    Reload
    ${promise} =    Promise To Upload File    ${OUTPUT_DIR}/upload/report.txt
    Click    id=upload
    Wait For    ${promise}
    Get Text    id=uploaded    ==    report.txt

Keyboard
    Click    id=keys
    Keyboard Key    press    a
    Get Text    id=key    ==    a
    Press Keys    id=keys    Enter
    Get Text    id=key    ==    Enter
    Keyboard Input    type    xyz
    Get Property    id=keys    value    ==    axyz

Mouse
    Click    id=counter
    Get Text    id=counter    ==    Clicks: 1
    Click With Options    id=counter    clickCount=2
    Get Text    id=counter    ==    Clicks: 3
    Hover    id=hover-target
    Get Text    id=hovered    ==    Hovered
    Reload
    Mouse Move Relative To    id=hover-target    0    0
    Get Text    id=hovered    ==    Hovered
    ${box} =    Get BoundingBox    id=counter
    Mouse Move    ${{ $box["x"] + 5 }}    ${{ $box["y"] + 5 }}
    Mouse Button    click
    Get Text    id=counter    ==    Clicks: 1
    Focus    id=name
    Get Element States    id=name    contains    focused

Drag And Drop
    Drag And Drop    id=drag-source    id=drop-target
    Get Text    id=dropped    ==    Dropped

Scrolling
    Scroll By    id=scroller    vertical=100
    # A fractional display scale can round the offset to whole device pixels.
    Get Scroll Position    id=scroller    top    validate    abs(value - 100) < 1
    Scroll To    id=scroller    vertical=0
    Get Scroll Position    id=scroller    top    ==    0
    Hover    id=scroller
    Mouse Wheel    0    50
    Get Scroll Position    id=scroller    top    >    0
    Scroll To Element    id=download

Screenshots
    ${path} =    Take Screenshot    filename=keywords-window
    File Should Exist    ${path}
    ${path} =    Take Screenshot    filename=keywords-heading    selector=id=heading
    File Should Exist    ${path}
    ${path} =    Take Screenshot    filename=keywords-full    fullPage=True    mask=id=table
    File Should Exist    ${path}
    ${base64} =    Take Screenshot    return_as=base64
    Should Not Be Empty    ${base64}

Page Changes
    Add Style Tag    \#heading { color: rgb(255, 0, 0) !important; }
    Get Style    id=heading    color    ==    rgb(255, 0, 0)
    ${count} =    Highlight Elements    css=button    duration=0s
    Should Be True    ${count} > 5

Console And Page Errors
    Evaluate JavaScript    ${None}    () => console.log('Hello from the window')
    Get Console Log    validate    any(message["text"] == "Hello from the window" for message in value)
    Evaluate JavaScript    ${None}    () => { setTimeout(() => { throw new Error('Error from the window'); }); }
    Get Page Errors    validate    any("Error from the window" in error["message"] for error in value)

Coverage
    Start Coverage    path=${OUTPUT_DIR}/coverage
    Click    id=counter
    ${report} =    Stop Coverage
    File Should Exist    ${report}
