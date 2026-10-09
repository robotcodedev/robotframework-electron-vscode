# Design

## Context

See proposal.md for motivation and the spec delta for the requirements.

The display profiles from `add-display-profiles` run their wrappers as shell scripts in `robot.toml`:
- `xvfb` runs `xvfb-run` with `SCREEN_SIZE`.
- `xephyr` starts Xephyr on a free display, runs the tests with `DISPLAY` set to it, and ends it afterwards.

Findings from 2026-10-09 with VS Code 1.141 on a 1920×1080 Xvfb screen:
- **Without a window manager:** the window stays 1200×800. Neither `window.newWindowDimensions` set to `maximized` nor `fullscreen` changes that, and neither does F11.
- **With Openbox:** started in the background before the tests, Openbox makes `maximized` fill the screen at 1920×1080, inside and out. The window has no frame, because VS Code uses its own title bar.
- **Cleanup:** Openbox ends by itself when its X server ends.
- **Screenshots and videos:** Playwright takes both from the page, not from the X screen, so they have the window's size. A video whose `size` is larger than the window shows a grey margin.

## Goals / Non-Goals

**Goals:**
- Maximised windows on the virtual displays, as on a desktop.
- No hard dependency: runs without Openbox keep working.

**Non-Goals:**
- A window manager for `local`; the desktop has one.
- Configuring Openbox. Its defaults are enough.
- Maximising other Electron applications. That is up to the application or the test.

## Decisions

### Openbox in the wrappers

Openbox is small, needs no configuration, and is packaged as `openbox` on Debian, Ubuntu, Fedora and Arch Linux. The wrappers start it in the background on their display only if it is installed:

- `xvfb`: `xvfb-run … sh -c 'command -v openbox >/dev/null && openbox & exec "$@"' wm "$@"`. The inner shell runs on the Xvfb display, starts Openbox there, and replaces itself with the test run.
- `xephyr`: after Xephyr reports its display, `command -v openbox >/dev/null && DISPLAY=":$display" openbox &` before the test run.

Openbox ends with its X server, so neither wrapper has to stop it.

### Maximised VS Code in the example

`Open Example VS Code` passes `settings=${{ {"window.newWindowDimensions": "maximized"} }}`. On the desktop, the desktop's window manager maximises it as well. The library's defaults stay unchanged, because maximising is a choice of the project.

### Documentation

- **CI guide:** both profiles start Openbox when it is installed, and VS Code needs `window.newWindowDimensions: maximized` to fill the screen.
- **Prerequisites:** the example's README gets a section *Prerequisites*, and the root README and AGENTS.md a line on the Linux packages for the display profiles:
  - Xvfb for `xvfb`: `xvfb` on Debian and Ubuntu, `xorg-server-xvfb` on Arch Linux;
  - Openbox for maximised windows: `openbox`;
  - Xephyr for `xephyr`: `xserver-xephyr` on Debian and Ubuntu, `xorg-server-xephyr` on Arch Linux.
  They say that the tests also pass without Openbox, with smaller windows.
- **Video guide:** the full-frame recipe becomes a run with `-p xvfb`, VS Code maximised and `record_video` with the screen size. `Set Viewport Size` stays as the way without a window manager.

## Risks / Trade-offs

- [VS Code opens its window before Openbox is ready] → VS Code takes about a second to start, and Openbox manages windows that already exist when it starts. The acceptance tests and the example check it on every run.
- [Openbox changes how other applications look] → Electron applications with a native frame get an Openbox title bar under `xvfb` and `xephyr`, which matters only for screenshots. The Electron acceptance tests check that their behaviour is unchanged.
