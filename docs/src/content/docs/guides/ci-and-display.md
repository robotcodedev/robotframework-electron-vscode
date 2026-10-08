---
title: CI and the Linux display
description: Run Electron and VS Code tests without a desktop, under Xvfb, and hidden on a Wayland desktop.
---

Electron applications and VS Code open real windows, so the tests need a display. On Windows and macOS they run as they are. On Linux, it depends on where the tests run.

## Linux without a desktop

On CI and other machines without a desktop, run the tests under a virtual X server with `xvfb-run`:

```sh
xvfb-run -a robot tests
```

`-a` picks a free display number, so several runs can use Xvfb at the same time. With RobotCode, put `xvfb-run -a` in front in the same way:

```sh
xvfb-run -a robotcode robot tests
```

## Linux with a Wayland desktop

On a Wayland desktop, Electron applications and VS Code follow `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE` and open their windows on the desktop, even under `xvfb-run`. To keep them hidden in Xvfb, remove `WAYLAND_DISPLAY` and set the session type to X11:

```sh
env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 xvfb-run -a robot tests
```

## Downloads on CI

`Open VS Code` and `Get Electron Executable` download VS Code and Electron on first use and cache them in the user's cache directory. To keep the downloads between CI runs, cache that directory, or give the keywords a `cache_dir` that the CI caches. [Downloads and cache](../downloads-and-cache/) shows how to pass it as a variable.
