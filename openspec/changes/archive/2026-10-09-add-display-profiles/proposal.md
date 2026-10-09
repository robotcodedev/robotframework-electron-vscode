# Proposal

## Why

Electron applications and VS Code need a display. Today every command in AGENTS.md, the README and the guides carries a long prefix such as `env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 xvfb-run -a`, and screenshots need a larger Xvfb screen on top of that. RobotCode's `robot.toml` has a `wrapper` setting, a command prefix per profile, and profiles can be bound to a platform with `enabled.if`. On 2026-10-08, a profile with this wrapper ran VS Code hidden on a Full HD Xvfb screen from a Wayland desktop, without any prefix on the command line. A Xephyr wrapper ran it visibly in a separate Full HD window.

## What Changes

- Display profiles in the repository's `robot.toml` and in the example's `robot.toml`:
  - `xvfb` (Linux only): hidden on a Full HD Xvfb screen, for CI and screenshots.
  - `xephyr` (Linux only): visible in a separate Full HD Xephyr window on the desktop, through a short shell script inline in `robot.toml`.
  - `local` (all platforms): no wrapper, on the normal desktop.
- No default profile: without `-p`, tests run on the desktop as before. Display profiles combine with others, for example `-p xvfb -p vscode-insiders`.
- AGENTS.md, the root README and the example's README use the profiles instead of the prefixes.
- The CI guide explains the profiles, Xvfb's default screen size of 640×480, and the plain `xvfb-run` prefix for runs without RobotCode.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-examples`: the example offers the display profiles.

## Impact

- `robot.toml`, `AGENTS.md`, `README.md`.
- `examples/vscode-extension/robot.toml` and the example's `README.md`.
- `docs/src/content/docs/guides/ci-and-display.md`.
- `extend-vscode-examples` uses `-p xvfb` for its screenshots.
