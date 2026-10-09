# VS Code extension example

A small VS Code extension with Robot Framework tests that drive the VS Code workbench: they run a command through the command palette, select a quick pick item, check notifications, and act inside a webview. Copy the folder as a starting point for your own extension's tests.

The `VSCode` library only downloads and starts VS Code. The keywords and locators for the workbench are part of this example, in `tests/resources/`, one resource per workbench part. Your project owns them and adapts them when VS Code changes.

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

The profile `locator-override` in `robot.toml` shows how a project overrides locators, for example per VS Code version:

```sh
robotcode -p locator-override robot
```

## Learn more

- [Writing your own workbench keywords](https://example.github.io/guides/workbench-keywords/) explains the resources.
- [VS Code versions and profiles](https://example.github.io/guides/vscode-versions/) explains the profiles in `robot.toml`.
