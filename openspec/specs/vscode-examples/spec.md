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
The repository SHALL provide an example project, `examples/vscode-extension`, whose own resources define keywords for running a command through the command palette, selecting a quick pick item, reading notifications and acting inside a webview.

#### Scenario: Command through the command palette
- **WHEN** the example runs a command of its extension with its palette keyword
- **THEN** the keyword waits for the command's row before it presses Enter, and the command's notification appears

#### Scenario: Quick pick
- **WHEN** the example selects an item of a quick pick that its extension shows
- **THEN** the extension receives that item, and its notification names it

#### Scenario: Webview
- **WHEN** the example enters its extension's webview and leaves it again
- **THEN** Browser keywords act inside the webview in between, and on the workbench afterwards

### Requirement: Locators as variables
The example's locators SHALL be variables of its resources, so that a project can override them per VS Code version in `robot.toml` without changing any keyword.

#### Scenario: Locator overridden by a profile
- **WHEN** the example runs with a profile that sets a locator variable
- **THEN** the example's keywords use the locator from the profile

### Requirement: Guides show the example
The documentation site SHALL have a guide on writing your own workbench keywords and locators and a guide on profiles per VS Code version, both of which include the example's files. The example SHALL keep the keywords and locators of each workbench part in a resource file of its own, so that a guide section shows a whole file.

#### Scenario: Guide on workbench keywords
- **WHEN** the documentation site is built
- **THEN** the guide on workbench keywords shows the example's resources for the command palette, quick picks, notifications and webviews, each from its file in `examples/vscode-extension`

#### Scenario: Guide on VS Code versions
- **WHEN** the documentation site is built
- **THEN** the guide on profiles per VS Code version shows the example's `robot.toml` with its profile from `examples/vscode-extension`

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
The example's `robot.toml` SHALL offer the profiles `xvfb`, which runs hidden on a Full HD Xvfb screen, and `xephyr`, which runs in a separate Full HD Xephyr window, both enabled only on Linux, and `local`, which runs on the normal desktop on every platform. A profile `small-screen` SHALL show how a profile changes the screen size of `xvfb` and `xephyr`.

#### Scenario: Hidden run from a Wayland desktop
- **WHEN** the example runs with `-p xvfb` on a Linux desktop with Wayland
- **THEN** no window opens on the desktop, and the tests see a 1920×1080 screen

#### Scenario: Visible run in a separate window
- **WHEN** the example runs with `-p xephyr` on a Linux desktop
- **THEN** the tests run in a 1920×1080 Xephyr window, and the Xephyr server has ended when the run ends

#### Scenario: Screen size from a profile
- **WHEN** the example runs with `-p xvfb -p small-screen`
- **THEN** the tests see a 1280×800 screen

#### Scenario: Other platforms
- **WHEN** the profiles are listed on Windows or macOS
- **THEN** only `local` and the example's other profiles are available
