# VS Code extension example

A small VS Code extension with Robot Framework tests that drive the VS Code workbench. Copy the folder as a starting point for your own extension's tests. The tests:

- run a command through the command palette, select a quick pick item, check notifications and act inside a webview (`commands.robot`, `quick_pick.robot`, `webview.robot`);
- open, edit and save files of a workspace, also through VS Code's own file dialog (`editor.robot`);
- run a command in the integrated terminal and read its output (`terminal.robot`);
- open a second window (`windows.robot`);
- run a Python script with the Python extension, installed when VS Code starts and into the running VS Code (`python.robot`);
- record a video of a demonstration of the extension, in the size of the screen and with presenter mode (`video.robot`).

Each VS Code opens a fresh copy of `tests/workspace` in the output directory, so the tests can change files.

The `VSCode` library only downloads and starts VS Code. The keywords and locators for the workbench are part of this example, in `tests/resources/`, one resource per workbench part. Your project owns them and adapts them when VS Code changes.

## Prerequisites

- Python with `robotframework-vscode` and RobotCode.
- For `python.robot`: network access for the Marketplace, which downloads the Python extension (about 100 MB per test), and a Python interpreter on the `PATH`.
- On Linux, for the display profiles in `robot.toml`:
  - Xvfb for `xvfb`: the package `xvfb` on Debian and Ubuntu, `xorg-server-xvfb` on Arch Linux;
  - Xephyr for `xephyr`: `xserver-xephyr` or `xorg-server-xephyr`;
  - the window manager Openbox, package `openbox`, so that VS Code opens maximised there. Without it, the tests still pass, with a smaller window.

## Running

From this folder, with `robotframework-vscode` installed:

```sh
robotcode robot
```

From the root of the `robotframework-vscode-testing` repository:

```sh
uv run robotcode -r examples/vscode-extension robot
```

On Linux, `robotcode -p xvfb robot` runs the tests hidden on a Full HD Xvfb screen, also on a Wayland desktop, and `robotcode -p xephyr robot` in a separate Xephyr window. Add `-p small-screen` for a 1280×800 screen instead. The first run downloads VS Code 1.141.0 into the user's cache directory. To use an installed VS Code instead, set `VSCODE_EXECUTABLE` in a personal `.robot.toml` next to `robot.toml`:

```toml
[variables]
VSCODE_EXECUTABLE = "/usr/share/code/code"
```

The tests in `python.robot` are tagged `network`. Leave them out with `-e network`, for example when there is no network access:

```sh
robotcode -p xvfb robot -e network
```

The tests take screenshots at their important steps, which the log shows and which are kept in `results/browser/screenshot/`. The video of `video.robot` is in `results/browser/video/`, and the log embeds it as well.

The profile `locator-override` in `robot.toml` shows how a project overrides locators, for example per VS Code version:

```sh
robotcode -p locator-override robot
```

## Learn more

- [Writing your own workbench keywords](https://example.github.io/guides/workbench-keywords/) explains the resources.
- [VS Code versions and profiles](https://example.github.io/guides/vscode-versions/) explains the profiles in `robot.toml`.
- [Dependency extensions](https://example.github.io/guides/extensions/) explains `python.robot`.
