# Spec Delta

## MODIFIED Requirements

### Requirement: Examples for driving the workbench
The repository SHALL provide an example project, `examples/vscode-extension`, whose own resources define keywords for running a command through the command palette, selecting a quick pick item, reading notifications, acting inside a webview, opening and editing files, using VS Code's file dialog and reading the terminal.

#### Scenario: Command through the command palette
- **WHEN** the example runs a command of its extension with its palette keyword
- **THEN** the keyword waits for the command's row before it presses Enter, and the command's notification appears

#### Scenario: Quick pick
- **WHEN** the example selects an item of a quick pick that its extension shows
- **THEN** the extension receives that item, and its notification names it

#### Scenario: Webview
- **WHEN** the example enters its extension's webview and leaves it again
- **THEN** Browser keywords act inside the webview in between, and on the workbench afterwards

#### Scenario: Edit and save a file
- **WHEN** the example opens a workspace file through Quick Open, types text into the editor and saves it
- **THEN** the file in the instance's workspace contains the text

#### Scenario: File dialog
- **WHEN** the example opens a file through VS Code's own file dialog
- **THEN** the file is open in the active editor

#### Scenario: Terminal
- **WHEN** the example runs a command in the integrated terminal
- **THEN** its keyword reads the command's output from the terminal

#### Scenario: Second window
- **WHEN** the example opens a new VS Code window and switches to the new page
- **THEN** Browser keywords act on the new window, and after closing it on the first window again

### Requirement: Guides show the example
The documentation site SHALL have a guide on writing your own workbench keywords and locators, a guide on profiles per VS Code version and a guide on dependency extensions, all of which include the example's files. The example SHALL keep the keywords and locators of each workbench part in a resource file of its own, so that a guide section shows a whole file.

#### Scenario: Guide on workbench keywords
- **WHEN** the documentation site is built
- **THEN** the guide on workbench keywords shows the example's resources for every workbench part, each from its file in `examples/vscode-extension`, and explains how to find locators with the RobotCode REPL

#### Scenario: Guide on VS Code versions
- **WHEN** the documentation site is built
- **THEN** the guide on profiles per VS Code version shows the example's `robot.toml` with its profile from `examples/vscode-extension`

#### Scenario: Guide on dependency extensions
- **WHEN** the documentation site is built
- **THEN** the guide on dependency extensions shows the example's Python suite from `examples/vscode-extension`

## ADDED Requirements

### Requirement: Fresh workspace per instance
The example SHALL open every VS Code instance on a fresh copy of its workspace in the run's output directory.

#### Scenario: Repository stays unchanged
- **WHEN** the example's tests have changed and moved files in the workspace
- **THEN** the workspace in `examples/vscode-extension` is unchanged

### Requirement: Dependency extensions in the example
The example SHALL show a Marketplace extension that the extension under test depends on, `ms-python.python`, both installed when VS Code starts and installed into a running instance.

#### Scenario: Installed at the start
- **WHEN** the example opens VS Code with `ms-python.python` in `extensions` and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

#### Scenario: Installed while running
- **WHEN** the example installs `ms-python.python` into a running instance with `Install VS Code Extension` and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

### Requirement: Screenshots in the documentation
The example's tests SHALL take screenshots at their important steps. A script SHALL run the example and copy selected screenshots into the documentation site, and the copied screenshots SHALL be committed.

#### Scenario: Regenerate the screenshots
- **WHEN** the screenshot script runs after the workbench has changed
- **THEN** the site's screenshots show the workbench as the example's tests see it now

### Requirement: Guide on Browser features
The documentation site SHALL have a guide that lists which Browser features work with VS Code, which need a setting, and which do not work.

#### Scenario: A feature that does not work
- **WHEN** someone looks up `Save Page As PDF` in the guide
- **THEN** the guide says that it does not work with VS Code and why
