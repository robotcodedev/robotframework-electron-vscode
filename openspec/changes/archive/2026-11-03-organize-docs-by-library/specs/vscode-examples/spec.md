# Spec Delta

## MODIFIED Requirements

### Requirement: Guide on Browser features
The VS Code section of the documentation site SHALL have a page on Browser keywords in VS Code. It SHALL list the Browser features that need a setting in VS Code, and those that work differently in VS Code than in other Electron applications, and link to the guide on Browser keywords in applications for everything else.

#### Scenario: A feature that does not work
- **WHEN** someone looks up `Save Page As PDF` for VS Code
- **THEN** the page on Browser keywords in VS Code leads to the guide on Browser keywords in applications, which says that it does not work and why

#### Scenario: A feature that needs a setting
- **WHEN** someone looks up `Drag And Drop` in the explorer
- **THEN** the page on Browser keywords in VS Code names the setting `explorer.confirmDragAndDrop`

### Requirement: Video of a test
The example SHALL have a test that records a video of VS Code while it demonstrates the extension, and one that records a video while it creates a Python script and runs it with the Python extension, both with the video's size taken from the screen size of the display profiles. A third test SHALL record the Python script without presenter mode, creating the file in the explorer. The page on videos and traces in the VS Code section SHALL include these tests from the example.

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
- **THEN** the page on videos and traces in the VS Code section shows the example's `video.robot` from `examples/vscode-extension`

### Requirement: Traces of tests
The example SHALL have a suite that records a Playwright trace of a test and a HAR file of a webview's network traffic. The page on videos and traces in the VS Code section SHALL include this suite from the example, and the guide on traces and HAR files SHALL explain how to open a trace.

#### Scenario: Traces of the example
- **WHEN** the example's tracing suite runs with `-p xvfb`
- **THEN** a trace of each test is in `browser/traces` of the output directory, and the HAR file of the webview test contains the webview's requests

#### Scenario: Guide on traces
- **WHEN** the documentation site is built
- **THEN** the page on videos and traces in the VS Code section shows the example's `tracing.robot` from `examples/vscode-extension`
