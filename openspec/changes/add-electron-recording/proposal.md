# Proposal

## Why

A video of a test run shows what happened, especially when a test fails on CI, and it is a good way to demonstrate an extension. Browser records videos for its own contexts (`recordVideo` of `New Context`), stores them in the output directory and embeds them in the log. `New Electron Application` starts applications through Playwright's `_electron.launch`, which supports the same recording, but the keyword passes no recording options. A test on 2026-10-08 recorded VS Code 1.141 through `_electron.launch` as a Full HD WebM, with Playwright's overlay of the performed actions.

## What Changes

- `New Electron Application` gets an argument `record_video` with Browser's `recordVideo` keys `dir` and `size`, plus Playwright's `showActions`. It passes them to `_electron.launch`.
- Like Browser, it resolves the default folder and size, returns the video's path in the page details, and embeds the video in the log. It reuses Browser's own helpers for this. The video is complete once the application has closed.
- `Open VS Code` passes `record_video` on to `New Electron Application`.
- The documentation explains recording, Playwright's ffmpeg, and why `Set Viewport Size` is needed for a full frame: VS Code's window does not fill an Xvfb screen. Browser's presenter mode serves as a slow motion, because Playwright has no `slowMo` for Electron.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: video recording of an application's windows.
- `vscode-launch`: `Open VS Code` records videos the same way.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, and `packages/vscode/src/VSCode/__init__.py`.
- Tests in both packages. Recording needs Playwright's ffmpeg, which comes with Browser's browsers and is present in the Browser clone.
- `docs/`: a guide section on videos and slow motion.
