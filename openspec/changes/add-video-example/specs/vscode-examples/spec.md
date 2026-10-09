# Spec Delta

## ADDED Requirements

### Requirement: Video of a test
The example SHALL have a test that records a video of VS Code while it demonstrates the extension, with the video's size taken from the screen size of the display profiles. The video guide SHALL include this test from the example.

#### Scenario: Video of the demonstration
- **WHEN** the example's video test runs with `-p xvfb`
- **THEN** a 1920×1080 video exists at the path in the page details after VS Code has closed, VS Code fills its frame, and the log embeds it

#### Scenario: Video in the screen size of a profile
- **WHEN** the example's video test runs with `-p xvfb -p small-screen`
- **THEN** the video is 1280×800, and VS Code fills its frame

#### Scenario: Guide on videos
- **WHEN** the documentation site is built
- **THEN** the guide on videos shows the example's `video.robot` from `examples/vscode-extension`
