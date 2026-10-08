# Spec Delta

## ADDED Requirements

### Requirement: Display profiles
The example's `robot.toml` SHALL offer the profiles `xvfb`, which runs hidden on a Full HD Xvfb screen, and `xephyr`, which runs in a separate Full HD Xephyr window, both enabled only on Linux, and `local`, which runs on the normal desktop on every platform.

#### Scenario: Hidden run from a Wayland desktop
- **WHEN** the example runs with `-p xvfb` on a Linux desktop with Wayland
- **THEN** no window opens on the desktop, and the tests see a 1920×1080 screen

#### Scenario: Visible run in a separate window
- **WHEN** the example runs with `-p xephyr` on a Linux desktop
- **THEN** the tests run in a 1920×1080 Xephyr window, and the Xephyr server has ended when the run ends

#### Scenario: Other platforms
- **WHEN** the profiles are listed on Windows or macOS
- **THEN** only `local` and the example's other profiles are available
