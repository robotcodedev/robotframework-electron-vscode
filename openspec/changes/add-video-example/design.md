# Design

## Context

See proposal.md for motivation and the spec delta for the requirements.
- **Recording:** `record_video` in `Open VS Code` takes `dir`, `size` and `showActions`. A window keeps its own size in the video: a larger window is scaled down, and a smaller one gets a grey margin.
- **Window size:** the example opens VS Code maximised. Under the display profiles `xvfb` and `xephyr`, Openbox maximises it to the screen, whose size `SCREEN_SIZE` sets, default `1920x1080`. `small-screen` sets `1280x800` with `extend-env`, so the variable is in the environment of the test run.
- **Slow motion:** presenter mode is Browser's slow motion: before every keyword with a selector, it highlights the element and waits. Keyboard keywords are not slowed down.

## Goals / Non-Goals

**Goals:**
- A copyable test that records a video that is easy to follow.
- The video guide shows code that the example runs.

**Non-Goals:**
- Videos in the documentation site. Videos are large, and the screenshots show the same states.
- Recording every test. A project switches recording on where it needs it, for example for demonstrations or failing CI runs.

## Decisions

### `video.robot`

- **Size:** a keyword in the suite reads `%{SCREEN_SIZE=1920x1080}`, splits it into width and height, and opens VS Code through `Open Example VS Code` with `record_video` set to that size and with `showActions` (800 ms, top right). On the normal desktop, without a display profile, VS Code is maximised to the desktop, and a larger window is scaled down to fit the video.
- **Steps:** the test turns on presenter mode with a duration of one second, then runs *Say Hello* and checks its notification, picks *Banana* in the quick pick, and clicks the button in the webview.
- **Check:** after `Close VS Code`, the test checks that the video file is not empty. Playwright finishes the file only when the application closes.
- **Cleanup:** the teardown restores the previous presenter mode, because `Set Presenter Mode` changes it for the whole run.
- **Resources:** the test uses the existing resources for the command palette, quick picks, notifications and webviews. It needs no network access.

### `Open Example VS Code`

It returns what `Open VS Code` returns: browser id, context id and page details. The page details contain the video's path. Existing tests ignore the return value.

### Guide

`videos.md` becomes `videos.mdx` and includes `video.robot` with `<Code>` in place of its full-frame snippet. The text around it explains maximising, `SCREEN_SIZE` and presenter mode. The paragraph on `Set Viewport Size` without a window manager, the ffmpeg section and the Electron snippet stay.

## Risks / Trade-offs

- [The screenshot script runs the video test as well] → It takes a few seconds and needs no network; the screenshots are not affected.
- [`SCREEN_SIZE` is not a valid `WxH` value] → The keyword fails when it splits the value, with a message that names it. The display profiles already depend on the same format.
