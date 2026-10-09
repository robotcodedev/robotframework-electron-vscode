# Design

## Context

See proposal.md for motivation and the spec delta for the requirements. RobotCode 2.7.0 supports these profile keys:
- **`wrapper`:** a command prefix for the test run. RobotCode appends its own command line to it.
- **`enabled.if`:** a Python expression that switches a profile on, for example `platform.system() == 'Linux'`.
- **`env`:** sets environment variables, but cannot remove one.

Electron and VS Code follow `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE`, so a hidden run on a Wayland desktop has to remove `WAYLAND_DISPLAY`.

Both wrappers were tried on 2026-10-08 with a copy of the example. The Xephyr test ran inside an Xvfb, so that no window opened on the desktop.

## Goals / Non-Goals

**Goals:**
- One short, platform-aware way to choose where tests run, identical in the repository and in the example.
- Full HD for hidden runs, which screenshots and videos need.

**Non-Goals:**
- Hidden runs on Windows or macOS. Electron needs a real desktop there.
- A default profile. With `default-profiles`, every explicit `-p` would drop the display profile silently.
- Other X servers such as Xpra or Xvnc.

## Decisions

### Profiles

```toml
[profiles.xvfb]
description = "Run hidden on a Full HD Xvfb screen (Linux)"
enabled.if = "platform.system() == 'Linux'"
wrapper = ["sh", "-c", '''
env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 xvfb-run -a -s "-screen 0 ${SCREEN_SIZE:-1920x1080}x24" "$@"
''', "xvfb-run"]

[profiles.xephyr]
description = "Run in a separate Full HD Xephyr window on the desktop (Linux)"
enabled.if = "platform.system() == 'Linux'"
wrapper = ["sh", "-c", '''<the Xephyr script below>''', "xephyr-run"]

[profiles.local]
description = "Run on the normal desktop"
```

- **Environment:** `env -u` sits in the wrapper because `env` in `robot.toml` can only set variables, and `WAYLAND_DISPLAY` must be removed.
- **Screen size:** both wrappers read `SCREEN_SIZE`, default `1920x1080`. Because they run as shell scripts, the variable can come from the shell or from a profile's `extend-env`, which RobotCode applies before it starts the wrapper. A plain command list would not expand it.
- **`small-screen`:** only in the example. It sets `SCREEN_SIZE` to `1280x800` with `extend-env`, which keeps the variables of other selected profiles where `env` would replace them, and is combined with `xvfb` or `xephyr`, to show how a project changes the size in `robot.toml`.
- **`local`:** it is empty on purpose. It makes the desktop an explicit choice in RobotCode's profile selection, for example in VS Code's test explorer.

### The Xephyr wrapper

A relative wrapper path is resolved against the folder `robotcode` is started from, not against the project root, and RobotCode's expressions do not know the project root. A script file would therefore only work when RobotCode starts in the project's folder. The wrapper is instead a short POSIX shell script inline in `robot.toml`, run as `sh -c '<script>' xephyr-run`. RobotCode appends its command line, which the script receives as `"$@"`. The script:
- It starts `Xephyr -displayfd` on a free display, with the size from `SCREEN_SIZE` (default `1920x1080`) and the window title "Robot Framework".
- It waits until Xephyr reports the display number.
- It runs the command with `DISPLAY` set, `WAYLAND_DISPLAY` removed and `XDG_SESSION_TYPE=x11`.
- A trap ends Xephyr when the run ends, so the run's exit status stays the command's.

The repository's and the example's `robot.toml` contain the same profiles, so the example stays self-contained, and both work from any folder.

### Documentation

- **AGENTS.md and README:** the commands become `uv run robotcode -r . -p xvfb robot`.
- **CI guide:**
  - the profiles as the RobotCode way;
  - `xvfb-run -a -s "-screen 0 1920x1080x24"` for plain `robot`;
  - the 640×480 default;
  - that VS Code's window does not fill the screen without `Set Viewport Size`.

## Risks / Trade-offs

- [Shell code inside `robot.toml` is harder to read than a script file] → It is six lines, with a comment that says what it does, and it avoids a path that depends on the starting folder.
- [Xephyr is not installed] → The script fails at once with the shell's "not found". The guide names the package.
- [`xvfb-run` and the `env -u` option are Linux tools] → The profiles are switched off on other platforms.
