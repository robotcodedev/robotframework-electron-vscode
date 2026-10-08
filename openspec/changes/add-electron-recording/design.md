# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements. Findings from 2026-10-08, with Playwright 1.63, Electron 44 and VS Code 1.141 under Xvfb:
- **Options:** `_electron.launch` accepts `recordVideo` with `dir`, `size` and `showActions`. Without `size`, the video is 800×600.
- **ffmpeg:** recording needs Playwright's ffmpeg. Browser sets `PLAYWRIGHT_BROWSERS_PATH=0` and finds the ffmpeg that comes with its browsers. Without ffmpeg, the first window never loads, so the start times out.
- **Window size:** VS Code's window is 1200×800 on a 1920×1080 Xvfb screen. Neither `window.newWindowDimensions` set to `maximized` nor to `fullscreen` changes that, because Xvfb has no window manager. `page.setViewportSize`, which is Browser's `Set Viewport Size`, makes the workbench fill a 1920×1080 video.
- **No `slowMo`:** Playwright has no `slowMo` for Electron. The browser options it creates for Electron do not contain one.
- **Presenter mode:** Browser's presenter mode highlights the element of every keyword with a selector and waits for its duration. It works with VS Code.

Browser already implements recording for `New Context`:
- `_set_video_path` resolves `dir` against its video folder `browser/video`.
- `_get_video_size` defaults the size to 1280×720.
- `context_cache` keeps the size per context.
- `_embed_video` writes a `<video>` element into the log and returns the path.

## Goals / Non-Goals

**Goals:**
- Videos of Electron applications and VS Code with the same keys, folder, default size and log embedding as Browser's `recordVideo`.
- Playwright's action overlay, which suits demonstrations.

**Non-Goals:**
- HAR recording and tracing. They are further launch or context options and can follow the same way in a later change.
- A slow motion of our own. Presenter mode covers it, and the guide explains it.
- Resizing windows automatically to the video size. Tests call `Set Viewport Size` when they want a full frame. This stays visible in the test, and Browser's keyword already does it.

## Decisions

### Argument

- `New Electron Application` gets the argument `record_video: RecordVideo | None = None`.
- `RecordVideo` is a `TypedDict` of the Electron library with Browser's keys `dir` and `size`, and with `showActions`, which has `duration`, `position`, `fontSize` and `cursor` as in Playwright.
- It is a type of our own because Browser's `RecordVideo` has no `showActions`, and Robot Framework would reject the unknown key. Whether Robot Framework accepts a nested dict for `showActions` without its own `TypedDict` is checked during implementation.

### Reusing Browser

- **Before the start:** the keyword resolves the options with Browser's own helpers on its `PlaywrightState` component, `_set_video_path` and `_set_video_size_to_int`, so the folder and the 1280×720 default match Browser's. It then passes them to `robotframeworkElectronLaunch`, which adds them as `recordVideo` to the launch options.
- **After the start:** it stores the size with `context_cache.add(context_id, size)`. The JS function returns `page.video()?.path()` of the first window, and Python embeds it with `_embed_video`, which returns the path for `NewPageDetails.video_path`.
- **Private helpers:** these are private methods of Browser. The library already relies on Browser internals through the `adoptContext` hook. The Browser clone pins the version, and the unit tests catch renamed helpers. If upstream objects, the helpers can be copied; they are about 30 lines.

### When the video is complete

Playwright writes the video when the page or the context closes. `Close Electron Application`, `Close Browser` and automatic closing all end the application through the context, so the file is complete afterwards. The log embeds the video from the start, as Browser's does, and the file appears at the end.

### VS Code

- `Open VS Code` gets `record_video` and passes it on.
- The guide shows the full-frame recipe: an Xvfb screen of `1920x1080x24`, `record_video` with `size` 1920×1080, and `Set Viewport Size    1920    1080` after `Open VS Code`.

## Risks / Trade-offs

- [Browser renames its private video helpers] → Unit tests call the keyword's option handling, so a renamed helper fails pytest at once.
- [No ffmpeg in a user's Browser installation] → Playwright then hangs until the start timeout. The keyword's documentation and the guide name ffmpeg, which `rfbrowser init` installs with the browsers. The keyword checks for it before the start only if that turns out to be simple, which is decided during implementation.
- [Videos are large] → Recording is opt-in, and the guide recommends it for demos and for failing CI runs.
