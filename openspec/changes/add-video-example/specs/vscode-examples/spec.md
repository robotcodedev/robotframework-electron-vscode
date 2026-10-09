# Spec Delta

## ADDED Requirements

### Requirement: Video of a test
The example SHALL have a test that records a video of VS Code while it demonstrates the extension, and one that records a video while it creates a Python script and runs it with the Python extension, both with the video's size taken from the screen size of the display profiles. A third test SHALL record the Python script without presenter mode, creating the file in the explorer. The video guide SHALL include these tests from the example.

#### Scenario: Video of the demonstration
- **WHEN** the example's video test runs with `-p xvfb`
- **THEN** a 1920×1080 video of it is in the output directory, VS Code fills its frame, and the log embeds it

#### Scenario: Video in the screen size of a profile
- **WHEN** the example's video test runs with `-p xvfb -p small-screen`
- **THEN** the video is 1280×800, and VS Code fills its frame

#### Scenario: Video of a Python script
- **WHEN** the example's second video test runs with `-p xvfb`
- **THEN** it creates `greeting.py` through VS Code's own Save As dialog, runs it with the run button above the editor, the terminal shows `Hello Robot Framework`, and the video shows it

#### Scenario: Video without presenter mode
- **WHEN** the example's video test without presenter mode runs with `-p xvfb`
- **THEN** it creates `greeting.py` in the explorer, runs it with the run button above the editor, the terminal shows `Hello Robot Framework`, and the video shows it

#### Scenario: Guide on videos
- **WHEN** the documentation site is built
- **THEN** the guide on videos shows the example's `video.robot` from `examples/vscode-extension`
