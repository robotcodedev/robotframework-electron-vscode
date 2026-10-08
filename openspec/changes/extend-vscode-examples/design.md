# Design

## Context

See proposal.md for motivation and the spec delta for the requirements. The example project in `examples/vscode-extension` has one resource per workbench part and its own `robot.toml`, and the guides include its files. The feature spike on 2026-10-08 used scratch suites and a RobotCode REPL session against VS Code 1.141 under Xvfb. It found:
- **Editor and dialogs:**
  - Quick Open (`Ctrl+P`), typing and saving work with keyboard keywords.
  - The editor's visible text is in `.view-lines`.
  - With `files.simpleDialog.enable`, *File: Open File...* shows VS Code's own dialog in the quick input, which Browser can use. Native dialogs are out of reach.
- **Terminal:** its rows are in `.xterm-rows`, also with the default renderer. The prompt comes from the user's shell configuration.
- **Python:** `extensions=["ms-python.python"]` installs the Python extension with its dependencies (Pylance, Python Environments, debugpy). *Python: Run Python File in Terminal* runs `hello.py` with the system Python and prints `Hello World` in the terminal.
- **Windows:** a new window is a new page. `Switch Page    NEW` and `Close Page` work.
- **Screen size:** `xvfb-run` uses a 640×480 screen by default. With `-s "-screen 0 1600x1000x24"`, the VS Code window is 1440×900, which suits screenshots.
- **Locator handlers** fire for notifications, but every wait for a notification triggers them as well, so a test of the handler itself cannot first check that the notification was there.

## Goals / Non-Goals

**Goals:**
- Examples for the parts most extension tests need: a project, the editor, the terminal, dependency extensions.
- Screenshots in the documentation that are regenerated from the example rather than taken by hand.
- An honest overview of which Browser features work with VS Code.

**Non-Goals:**
- Example tests for every Browser feature. Locator handlers, drag and drop, aria snapshots, the console log and coverage get short snippets in the Browser features guide.
- Windows support for the terminal example. Its command is POSIX shell, as on the CI the repository uses.
- Video, HAR and tracing. `New Electron Application` does not pass Playwright's recording options yet, which is a separate change.

## Decisions

### Workspace copy

- `tests/workspace/` holds `hello.py` and a text file.
- A keyword `Example Workspace` returns `${OUTPUT_DIR}/workspaces/${SUITE NAME}`. `Open Example VS Code` replaces that folder with a fresh copy of `tests/workspace` and opens it, and tests call `Example Workspace` when they check files.
- The path is computed when it is needed, so no suite or global variable is set. Tests of one suite that open their own instances, such as the two Python tests, get a fresh copy each time, because the previous instance has closed.

### `Open Example VS Code`

- It passes on any named arguments of `Open VS Code`, such as `extensions`, as `&{options}`.
- Its settings switch on `files.simpleDialog.enable`, and set `terminal.integrated.defaultProfile.linux` and `.osx` to `sh`. That keeps the terminal independent of personal shell configuration, in tests and in screenshots. The exact profile name is checked against VS Code 1.141.

### New resources

Each new resource covers one workbench part, has its locators as template variables filled with `Format String`, and imports what it uses, as the existing ones do:
- `editor.resource`:
  - `Open File    ${name}` opens a file through Quick Open, waits for its row, and then waits for the file's tab to be active.
  - `Save File` saves the active editor.
  - Shortcuts use Playwright's `ControlOrMeta`, so they also work on macOS.
- `file_dialog.resource`: `Open File With Dialog    ${path}` runs *File: Open File...*, replaces the path in the dialog's input and confirms.
- `terminal.resource`:
  - `Run In Terminal    ${command}` opens a new terminal and runs the command.
  - `Terminal Should Show    ${text}` waits until the active terminal shows the text.

### New suites

- `editor.robot`:
  - A test opens a file, types, saves, and checks the file on disk.
  - Another test opens a file through the dialog.
- `terminal.robot`: runs `echo $((40 + 2))` and waits for `42`. The number shows that the command ran, because it does not appear in the typed command line.
- `python.robot`: one test opens VS Code with `extensions=${{ ["ms-python.python"] }}`, and the other installs the extension with `Install VS Code Extension` after the start. Both open `hello.py`, run *Python: Run Python File in Terminal* and wait for `Hello World`. The suite needs network access and a Python interpreter, as its documentation says.
- `windows.robot`: opens a new window with `ControlOrMeta+Shift+N`, which avoids the palette, where *New Window* also matches *New Window with Profile*. It switches to the new page, checks the workbench there, closes it, and checks the first window.

### Screenshots

- **In the example:** the tests call `Take Screenshot    filename=<name>` at their important steps, so every run has the pictures in its log. The names are stable, for example `command-palette`, `quick-pick`, `webview`, `editor`, `terminal` and `python-run`.
- **Script:** `docs/scripts/update_screenshots.py` runs the example from the repository root. It uses `xvfb-run -a -s "-screen 0 1600x1000x24"` and removes `WAYLAND_DISPLAY`, so the run is hidden and the size is fixed. It then copies the selected screenshots from the run's `browser/screenshot` folder to `docs/src/assets/screenshots/`.
- **Committed:** the screenshots are committed, like the reference pages. The guides show them as Markdown images, which Astro optimises at build time.
- **AGENTS.md** says when to run the script: after changes to the example or to the VS Code version.

### Guides

- `workbench-keywords.mdx`: sections for the editor, the file dialog and the terminal, each with its resource, and a section *Finding locators* on the RobotCode REPL:
  - open the example's VS Code in `robotcode repl`;
  - look at `Get Aria Snapshot`;
  - try selectors with `Highlight Elements` and `Get Element Count`;
  - move what works into the resource.
- `extensions.mdx` (new): dependency extensions with `extensions` and `Install VS Code Extension`. It includes `python.robot` and the `python-run` screenshot.
- `browser-features.md` (new): a table of the spike's results with the categories *works*, *needs a setting* and *does not work*, plus short snippets for features without an example test. It is a Markdown table rather than generated content.
- `ci-and-display.md`: Xvfb's default screen size and the `-s` option.
- `getting-started/vscode.md`: the `command-palette` screenshot.

## Risks / Trade-offs

- [`Install VS Code Extension` with `ms-python.python` needs a reload because of its dependencies] → The spike tried a running install only with a small extension. The Python test checks it. If a reload is needed, the test reloads the window with *Developer: Reload Window*, and the extensions guide says so.
- [The Python tests download about 100 MB from the Marketplace per instance] → Accepted for the example. The guide mentions it, and the tests are tagged `network` so that offline runs can exclude them.
- [Screenshots in the repository go stale] → The script makes regenerating one command, and AGENTS.md names when to run it. Stale pictures do not break anything.
- [The terminal shows personal shell output despite `sh`, for example through `ENV`] → It is checked when the screenshots are generated; the setting can name `/bin/sh` with arguments if needed.
