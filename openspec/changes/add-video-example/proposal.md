# Proposal

## Why

`New Electron Application` and `Open VS Code` record videos with `record_video`, and the guide *Videos and slow motion* explains it with a snippet of its own. The example project has no test that records one, so users cannot copy a working setup. The guide's snippet is also the only larger piece of code in the guides that does not come from the example.

## What Changes

- **New suite:** `video.robot` in the example, with two tests that record a video. They switch on Browser's presenter mode, so the steps are slow enough to follow, and Playwright's action overlay.
  - One demonstrates the extension: a command with its notification, the quick pick and the webview.
  - The other installs the Python extension, creates a new file with `print("Hello Robot Framework")`, saves it as `greeting.py` through VS Code's own Save As dialog, and runs it with the run button above the editor. It needs network access like `python.robot`.
- **New keywords:** `New File` in `editor.resource`, `Save File With Dialog` in `file_dialog.resource`, and a `python.resource` with `Run Python File`, which clicks the run button above the editor once the Python extension is ready. `python.robot` uses it as well.
- **Explorer:** a new `explorer.resource` with `Create File In Explorer`, which `editor.robot` uses in a test of its own.
- **Video without presenter mode:** a third test in `video.robot` records the Python script without presenter mode and creates the file in the explorer.
- **Video size:** the size comes from `SCREEN_SIZE`, default `1920x1080`, which the display profiles use for the screen. VS Code opens maximised, so it fills the frame, also with `small-screen`.
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
