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
- **Steps:** the suite turns on presenter mode with a duration of one second. The test runs *Say Hello* and checks its notification, picks *Banana* in the quick pick, and clicks the button in the webview.
- **End:** the tests do not close VS Code and do not check the video file; they show how to record. Browser's automatic closing ends VS Code at the end of each test, which finishes the video, and in presenter mode it waits five seconds before, so that the video shows the result.
- **Presenter mode:** the suite setup switches it on and the suite teardown off, because `Set Presenter Mode` changes it for the whole run.
- **Resources:** the test uses the existing resources for the command palette, quick picks, notifications and webviews. It needs no network access.
- **Python script:** a second test, tagged `network`, opens VS Code with `extensions=["ms-python.python"]` and records as well. It creates `greeting.py` with `Create File In Explorer`, which opens it in the editor, types `print("Hello Robot Framework")`, saves it with `Save File`, and runs it with `Run Python File`. The terminal shows `Hello Robot Framework`.

### New keywords

- **`explorer.resource`:** `Create File In Explorer    ${name}` hovers over the explorer, which shows its *New File...* action only then, clicks it, fills the name into the input that the explorer shows in its tree, and presses Enter. VS Code creates the file and opens it in the editor. A first version saved a new, untitled file through the Save As dialog instead, which is a detour.
- **`python.resource`:** `Run Python File` clicks the run button that the Python extension shows above a Python file, instead of using the command palette. It first waits until the extension shows the chosen interpreter in the status bar and the progress *Discovering Python Interpreters* has gone: a click right after the interpreter appeared made the extension report an invalid interpreter and not run the file. It moves out of `python.robot`, which uses the resource now, so that both suites share it.
- **Stable run button:** under presenter mode the click failed now and then with "Adding selector recorder to page failed". VS Code redraws the run button several times while the Python extension starts, the last time about a second after the interpreter discovery has finished. Presenter mode scrolls to the element before the click without retrying, so a redrawn button fails with "Element is not attached to the DOM", and Browser then falls back to its selector recorder, which VS Code's Content Security Policy blocks. A plain `Click` would retry. `Run Python File` therefore waits with `Wait For Function` until the button has stayed the same element for two seconds, and clicks then.

### Guide

`videos.md` becomes `videos.mdx` and includes `video.robot` with `<Code>` in place of its full-frame snippet. The text around it explains maximising, `SCREEN_SIZE` and presenter mode. The paragraph on `Set Viewport Size` without a window manager, the ffmpeg section and the Electron snippet stay.

## Risks / Trade-offs

- [The screenshot script runs the video test as well] → It takes a few seconds and needs no network; the screenshots are not affected.
- [`SCREEN_SIZE` is not a valid `WxH` value] → The keyword fails when it splits the value, with a message that names it. The display profiles already depend on the same format.
