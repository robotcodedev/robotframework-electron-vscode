---
title: Videos and slow motion
description: Record videos of Electron applications and VS Code, and slow tests down with Browser's presenter mode.
---

A video shows what a test did, which helps when a test fails on CI, and it is a good way to demonstrate an extension.

## Recording a video

`New Electron Application` and `Open VS Code` record a video when they get `record_video`. The keys are those of Browser's `recordVideo` for `New Context`, plus Playwright's overlay of the performed actions:

- `dir`: the folder for the videos. Relative paths are relative to Browser's video folder `browser/video` in the output directory, which is also the default.
- `size`: the size of the video, as `width` and `height`. The default is 1280×720.
- `showActions`: shows each performed action in the video, with `duration` in milliseconds, `position` (for example `top-right`), `fontSize` and `cursor`.

An empty dictionary records with the defaults:

```robotframework
*** Settings ***
Library    Electron

*** Test Cases ***
Recorded Run
    New Electron Application    /opt/my-app/my-app    record_video={}
    Click    text=Say hello
    Close Electron Application
```

The log embeds the video, and the page details that the keyword returns contain its path. Playwright finishes the file when the application closes, through `Close Electron Application`, `Close VS Code`, `Close Browser` or Browser's automatic closing.

## A full frame of VS Code

A window keeps its own size in the video: a larger window is scaled down to fit, and a smaller one is shown at its own size with a grey margin. VS Code's window does not fill an Xvfb screen, and under Xvfb there is no window manager that could maximise it. `Set Viewport Size` with the size of the video makes the workbench fill the frame:

```robotframework
*** Settings ***
Library    VSCode

*** Test Cases ***
Extension Demo
    Open VS Code    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
    ...    record_video={'size': {'width': 1920, 'height': 1080}, 'showActions': {'duration': 800, 'position': 'top-right'}}
    Set Viewport Size    1920    1080
    Keyboard Key    press    F1
    Keyboard Input    type    Robot Test: Say Hello
    Wait For Elements State    .quick-input-list .monaco-list-row[aria-label*="Robot Test: Say Hello"]    visible
    Keyboard Key    press    Enter
    Get Text    .notifications-toasts .notification-list-item-message    ==    Hello Robot
    Close VS Code
```

## ffmpeg

Playwright needs its own ffmpeg to record. It is installed together with Browser's browsers, and with Playwright's `install chromium`. If Browser was set up without browsers, install it alone with Playwright's `install ffmpeg` command. Without ffmpeg, the application's first window does not load, and the start fails after its timeout.

## Slow motion

Playwright's `slowMo` is not available for Electron applications, because Playwright has no such option when it launches them. Browser's presenter mode serves instead. Before every keyword that takes a selector, it scrolls to the element, highlights it and waits for the given duration:

```robotframework
Set Presenter Mode    {'duration': '1s', 'color': 'red'}
Click    id=change
Set Presenter Mode    False
```

Keyboard keywords such as `Keyboard Input` have no selector and are not slowed down. Together with `showActions` in the video, presenter mode makes a demonstration easy to follow.
