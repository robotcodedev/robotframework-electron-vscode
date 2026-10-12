*** Settings ***
Documentation       Behaviour of Electron that differs from a web browser. The color scheme, the locale and the
...                 time zone are in launch_options.robot, the viewport in context_state.robot.
Resource            ../resources/fixture.resource

Test Setup          Start Fixture App    --page\=keywords.html
Test Teardown       Close Electron Application    ALL


*** Test Cases ***
Shortcuts Do Not Reach The Menu
    [Documentation]    Keyboard keywords reach the page, but not the accelerators of the application's menu.
    Press Keys    id=keys    ControlOrMeta+Shift+KeyG
    Get Text    id=key    ==    G
    Keyboard Key    press    ControlOrMeta+Shift+KeyG
    Get Attribute Names    body    validate    "data-menu" not in value
    Evaluate In Main Process    ({ Menu }) => Menu.getApplicationMenu().getMenuItemById('greet').click()
    Get Attribute    body    data-menu    ==    greet

Prompt Is Not Supported
    [Documentation]    Electron has no prompt(), so the prompt_input of Handle Future Dialogs never applies.
    Handle Future Dialogs    accept    prompt_input=Robot
    Click    id=prompt
    Get Text    id=dialog-result    ==    prompt() is not supported.
