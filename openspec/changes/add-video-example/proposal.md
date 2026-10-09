# Proposal

## Why

`New Electron Application` and `Open VS Code` record videos with `record_video`, and the guide *Videos and slow motion* explains it with a snippet of its own. The example project has no test that records one, so users cannot copy a working setup. The guide's snippet is also the only larger piece of code in the guides that does not come from the example.

## What Changes

- **New suite:** `video.robot` in the example. Its test records a video while it demonstrates the extension: a command with its notification, the quick pick and the webview. It switches on Browser's presenter mode, so the steps are slow enough to follow, and Playwright's action overlay.
- **Video size:** the size comes from `SCREEN_SIZE`, default `1920x1080`, which the display profiles use for the screen. VS Code opens maximised, so it fills the frame, also with `small-screen`.
- **`Open Example VS Code`:** returns the ids and page details of `Open VS Code`, so that tests can read the video's path.
- **Guide:** *Videos and slow motion* includes the example's suite instead of its own snippet.
- **README:** the example's README names the suite.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-examples`: a test of the example records a video.

## Impact

- `examples/vscode-extension/tests/video.robot` and `tests/resources/vscode.resource`, and the example's `README.md`.
- `docs/src/content/docs/guides/videos.md`, which becomes `videos.mdx`.
- The screenshot script runs the new test as well; it takes a few seconds longer.
