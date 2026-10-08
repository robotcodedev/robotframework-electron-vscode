# Tasks

## 1. Electron

- [ ] 1.1 Add `RecordVideo` and the argument `record_video` to `New Electron Application`. Resolve folder and size with Browser's helpers, pass `recordVideo` in `electron.js`, store the size in `context_cache`, and return and embed the video path with `_embed_video`. Add unit tests for the option handling, including the defaults (`browser/video`, 1280×720) and a `showActions` dict. Verify that `uv run pytest` passes.
- [ ] 1.2 Add acceptance tests with the fixture app for "Video of an application" (file exists after close, the log contains the `<video>` element), "Action overlay" (a recording with `showActions` succeeds) and "No recording by default". Verify that the Electron acceptance tests pass.

## 2. VS Code

- [ ] 2.1 Add `record_video` to `Open VS Code` and pass it on. Add an acceptance test for "Video of a VS Code instance". Verify that the VSCode acceptance tests pass, and that `uv run robotcode -r . analyze code` reports no errors or warnings.

## 3. Documentation

- [ ] 3.1 Add a guide `docs/src/content/docs/guides/videos.md` on recording (options, ffmpeg, the full-frame recipe with Xvfb and `Set Viewport Size`) and on presenter mode as slow motion. Verify its snippets in a RobotCode REPL session or a scratch suite, and that `npm run build` in `docs/` succeeds.
