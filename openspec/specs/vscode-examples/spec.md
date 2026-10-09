# vscode-examples Specification

## Purpose

Draws the line between the VSCode library and the user's project, and shows with runnable examples how a project drives the VS Code workbench. The library provides only the technique: downloading VS Code, isolated launch, and windows as Browser pages. Keywords and locators for workbench parts belong to the project.

## Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Open VS Code`, `Close VS Code` and `Install VS Code Extension`

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

### Requirement: Locators as variables
The example's locators SHALL be variables of its resources, so that a project can override them per VS Code version in `robot.toml` without changing any keyword.

#### Scenario: Locator overridden by a profile
- **WHEN** the example runs with a profile that sets a locator variable
- **THEN** the example's keywords use the locator from the profile

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

### Requirement: Examples run with the repository's tests
The examples SHALL run as part of the repository's tests, so that they keep working with the current libraries and VS Code.

#### Scenario: Example run
- **WHEN** `uv run robotcode -r examples/vscode-extension robot` runs from the repository root
- **THEN** all example tests pass

### Requirement: Self-contained template
The example SHALL be a self-contained extension project with its own `robot.toml`, which refers to nothing outside its folder, so that it can be copied as a starting point.

#### Scenario: Copied example
- **WHEN** the example folder is copied out of the repository and run from its own root, with the VSCode library installed
- **THEN** its tests pass

### Requirement: Display profiles
The example's `robot.toml` SHALL offer the profiles `xvfb`, which runs hidden on a Full HD Xvfb screen, and `xephyr`, which runs in a separate Full HD Xephyr window, both enabled only on Linux and both with a window manager on their display, and `local`, which runs on the normal desktop on every platform. A profile `small-screen` SHALL show how a profile changes the screen size of `xvfb` and `xephyr`. The example SHALL open VS Code maximised.

#### Scenario: Hidden run from a Wayland desktop
- **WHEN** the example runs with `-p xvfb` on a Linux desktop with Wayland
- **THEN** no window opens on the desktop, and the tests see a 1920×1080 screen

#### Scenario: Visible run in a separate window
- **WHEN** the example runs with `-p xephyr` on a Linux desktop
- **THEN** the tests run in a 1920×1080 Xephyr window, and the Xephyr server and its window manager have ended when the run ends

#### Scenario: Screen size from a profile
- **WHEN** the example runs with `-p xvfb -p small-screen`
- **THEN** the tests see a 1280×800 screen

#### Scenario: VS Code fills the screen
- **WHEN** the example opens VS Code with `-p xvfb` or `-p xephyr`
- **THEN** the VS Code window is as large as the screen

#### Scenario: Without a window manager
- **WHEN** the example runs with `-p xvfb` on a machine without Openbox
- **THEN** the tests pass, with VS Code at its default window size

#### Scenario: Other platforms
- **WHEN** the profiles are listed on Windows or macOS
- **THEN** only `local` and the example's other profiles are available

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
