# Tasks

## 1. Example

- [x] 1.1 Write `video.robot` with the video size from `SCREEN_SIZE`, the action overlay and presenter mode. Verify the scenarios "Video of the demonstration" (`ffprobe` for the size, a frame for the full window, the `<video>` element in `output.xml`, without a check in the test) and "Video in the screen size of a profile", and that `analyze code` reports no errors or warnings and the whole example still passes.
- [x] 1.2 Name the suite in the example's `README.md`.
- [x] 1.3 Add `python.resource` (moved out of `python.robot`), and the second video test, tagged `network`, that creates `greeting.py` and runs it. Verify the scenario "Video of a Python script" (terminal output, file content, video size and a frame), that `python.robot` still passes, and that `analyze code` reports no errors or warnings. Update the README and include `python.resource` in the extensions guide.
- [ ] 1.4 Create `greeting.py` with `Create File In Explorer` (`explorer.resource`) instead of the Save As dialog, and let `Run Python File` wait until the run button is no longer redrawn. Verify the video tests five times in a row with `-p xvfb -p small-screen`, and `python.robot` and the whole example once. Update the guides that include the changed files.

## 2. Documentation

- [x] 2.1 Turn `videos.md` into `videos.mdx` and include `video.robot` in place of the full-frame snippet. Verify the scenario "Guide on videos" with `npm run build`, with no broken links.
