# Robot Framework Electron & VS Code

[Robot Framework](https://robotframework.org) libraries for testing Electron applications and VS Code extensions, built on the [Browser library](https://robotframework-browser.org):

- [`robotframework-electron`](packages/electron/) (`Electron`) starts Electron applications. Their windows are ordinary Browser pages, and every Browser keyword works on them.
- [`robotframework-vscode`](packages/vscode/) (`VSCode`) downloads VS Code and starts isolated instances with the extension under test, for end-to-end tests of VS Code extensions.

The libraries provide the technique: starting the application and handing its windows to Browser. What to click and which locators to use belongs to your tests.

**Documentation:** https://example.github.io/

## Status

The libraries are in a pilot phase, at version 0.1.0, and not yet published on PyPI.

They need a small hook in the Browser library, `adoptContext`, which lets a Browser extension hand a Playwright context that it created itself to the Browser library. The hook is not part of a Browser release yet. Until it is, this repository takes `robotframework-browser` from a local clone with the hook.

## Development

The repository is a uv workspace with both libraries in `packages/`, the documentation site in `docs/`, and planned and archived changes in `openspec/`. `AGENTS.md` describes how to set up the Browser clone. Then, from the repository root:

```sh
uv sync                                            # install the workspace with the dev tools
uv run pytest                                      # unit tests
uv run robotcode -r . robot                                  # acceptance tests on the desktop, configured in robot.toml
uv run robotcode -r . -p xvfb robot                          # hidden on a Full HD Xvfb screen (Linux)
uv run robotcode -r . -p xephyr robot                        # in a separate Xephyr window (Linux)
uv run robotcode -r . -p xvfb -p electron-previous robot     # against an older Electron major
uv run robotcode -r . -p xvfb -p vscode-insiders robot       # against the newest VS Code Insiders
```

- The display profiles need Xvfb (`xvfb` or `xorg-server-xvfb`) and, for `xephyr`, Xephyr (`xserver-xephyr` or `xorg-server-xephyr`); with Openbox (`openbox`) installed, windows can be maximised there.
- The acceptance tests download Electron and VS Code into the repository's `.cache/`. To use local executables instead, set `ELECTRON_EXECUTABLE` or `VSCODE_EXECUTABLE` in a personal, gitignored `.robot.toml`:

  ```toml
  [variables]
  VSCODE_EXECUTABLE = "/path/to/code"
  ```

- The test `Application And Web Browser` needs Chromium for Playwright in the Browser clone, and the video tests need Playwright's ffmpeg: `PLAYWRIGHT_BROWSERS_PATH=0 npx playwright install chromium` there installs both.
- To run the VS Code tests against a fork, point `VSCODE_EXECUTABLE` at it and leave out the tests that check VS Code's own behaviour:

  ```sh
  uv run robotcode -r . -p xvfb robot -v VSCODE_EXECUTABLE:/opt/vscodium/codium -e vscode-only -bl "Electron & VSCode.VSCode"
  ```
