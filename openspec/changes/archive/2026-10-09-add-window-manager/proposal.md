# Proposal

## Why

Xvfb and Xephyr have no window manager, so applications cannot maximise their windows there. On a 1920×1080 Xvfb screen, VS Code keeps a 1200×800 window, and neither `window.newWindowDimensions` set to `maximized` or `fullscreen` nor F11 changes that. A window manager is what makes maximising possible. Playwright takes screenshots and videos of the page, so they have the window's size: a maximised window gives them the screen's size, a video recorded in that size has no grey margin, and a visible `xephyr` run fills its window. Without a window manager, the only way is `Set Viewport Size`, which emulates the size instead of changing the window. On 2026-10-09, with Openbox running in the Xvfb, VS Code with `window.newWindowDimensions: maximized` filled the whole 1920×1080 screen, without a frame, because VS Code draws its own title bar.

## What Changes

- **Window manager:** the display profiles `xvfb` and `xephyr` start Openbox on their display before the tests run, in the repository's and in the example's `robot.toml`. If Openbox is not installed, the tests still run, only without maximised windows. `local` stays unchanged, because the desktop has its own window manager.
- **Example:** `Open Example VS Code` opens VS Code maximised (`window.newWindowDimensions: maximized`), so it fills the screen under `xvfb` and `xephyr` and on the desktop.
- **Documentation:**
  - The CI guide names Openbox as an optional package.
  - The prerequisites for running the example and the repository's tests name Xvfb, Openbox and Xephyr with their packages: in the example's README, the root README and AGENTS.md.
  - The video guide's full-frame recipe uses the maximised window, and keeps `Set Viewport Size` for runs without a window manager.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-examples`: the display profiles run a window manager, and the example's VS Code fills the screen.

## Impact

- `robot.toml` and `examples/vscode-extension/robot.toml`: the `xvfb` and `xephyr` wrappers.
- `examples/vscode-extension/tests/resources/vscode.resource`: the setting in `Open Example VS Code`.
- `docs/src/content/docs/guides/ci-and-display.mdx` and `videos.md`.
- `examples/vscode-extension/README.md`, `README.md` and `AGENTS.md`: the Linux prerequisites.
- `extend-vscode-examples` no longer needs the `VSCODE_VIEWPORT` variable for its screenshots.
