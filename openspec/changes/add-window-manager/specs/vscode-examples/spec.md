# Spec Delta

## MODIFIED Requirements

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
