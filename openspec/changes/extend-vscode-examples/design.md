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
- **Screen size:** `xvfb-run` uses a 640×480 screen by default, and without a window manager VS Code keeps a 1200×800 window. The display profiles from `add-display-profiles` and `add-window-manager` give a Full HD screen with Openbox, and VS Code opened maximised fills it.
- **Locator handlers** fire for notifications, but every wait for a notification triggers them as well, so a test of the handler itself cannot first check that the notification was there.

## Goals / Non-Goals

**Goals:**
- Examples for the parts most extension tests need: a project, the editor, the terminal, dependency extensions.
- Screenshots in the documentation that are regenerated from the example rather than taken by hand.
- An honest overview of which Browser features work with VS Code.

**Non-Goals:**
- Example tests for every Browser feature. Locator handlers, drag and drop, aria snapshots, the console log and coverage get short snippets in the Browser features guide.
- Windows support for the terminal example. Its command is POSIX shell, as on the CI the repository uses.
- Videos in the example. The guide *Videos and slow motion* covers them; HAR and tracing are not available yet.

## Decisions

### Workspace copy

- `tests/workspace/` holds `hello.py` and a text file.
- A keyword `Example Workspace` returns `${OUTPUT_DIR}/workspaces/${SUITE NAME}`. `Open Example VS Code` replaces that folder with a fresh copy of `tests/workspace` and opens it, and tests call `Example Workspace` when they check files.
- The path is computed when it is needed, so no suite or global variable is set. Tests of one suite that open their own instances, such as the two Python tests, get a fresh copy each time, because the previous instance has closed.

### `Open Example VS Code`

- It passes on any named arguments of `Open VS Code`, such as `extensions`, as `&{options}`.
- Besides `window.newWindowDimensions: maximized` from `add-window-manager`, its settings switch on `files.simpleDialog.enable` and make the terminal run `sh`. VS Code 1.141 has no built-in profile `sh`, only `bash`, `fish`, `pwsh`, `tmux` and the like, so the settings define one in `terminal.integrated.profiles.linux` and `.osx` (`{"sh": {"path": "sh"}}`) and make it the default. That keeps the terminal independent of personal shell configuration, in tests and in screenshots.

### Changes to `Run Command` and the row locators

Two findings while writing the terminal test change the existing command palette and quick pick resources:
- **Late commands:** some commands, such as *Terminal: Create New Terminal*, are registered only a while after VS Code has started, and a palette that is already open does not show them, like the commands of an extension installed into a running instance. `Run Command` therefore opens a fresh palette until the command's row appears, within `${COMMAND_TIMEOUT}` (30 seconds), and each attempt waits two seconds. During the attempts it switches off Browser's run-on-failure keyword and restores it afterwards, so failed attempts leave no failure screenshots. The Python test needs no retry of its own.
- **Exact rows:** `aria-label*="{title}"` matched five rows for *Terminal: Create New Terminal*, for example *… (In Active Workspace)*, and Browser's strict mode failed. `:text-is()` does not help, because every row has a highlighted span with exactly the typed text. A row's `aria-label` is the title, or the title followed by `, ` and its key binding or a hint such as `similar commands`. The locators therefore match `[aria-label="{title}"]` or `[aria-label^="{title}, "]`, for palette rows and quick pick items, and the `locator-override` profile follows.

### New resources

Each new resource covers one workbench part, has its locators as template variables filled with `Format String`, and imports what it uses, as the existing ones do:
- `editor.resource`:
  - `Open File    ${name}` opens a file through Quick Open, waits for its row, and then waits for the file's tab to be active.
  - `Save File` saves the active editor.
  - Shortcuts use Playwright's `ControlOrMeta`, so they also work on macOS.
- `file_dialog.resource`: `Open File With Dialog    ${path}` runs *File: Open File...*, replaces the path in the dialog's input and confirms. The dialog lists its folder asynchronously and then sets the input to that folder, which overwrote a path filled in too early; the keyword therefore waits for the first listed entry and checks the input's value before it presses Enter.
- `terminal.resource`:
  - `Run In Terminal    ${command}` opens a new terminal and runs the command.
  - `Terminal Should Show    ${text}` waits until the active terminal shows the text.

### New suites

- `editor.robot`:
  - A test opens a file, types, saves, and checks the file on disk.
  - Another test opens a file through the dialog.
- `terminal.robot`: runs `echo $((40 + 2))` and waits for `42`. The number shows that the command ran, because it does not appear in the typed command line.
- `python.robot`: before it runs the Python extension's command, each test waits until the extension shows the chosen interpreter in the status bar. Run right after opening `hello.py`, the command failed with "Unable to find workspace for given file" while the extension was still starting. One test opens VS Code with `extensions=${{ ["ms-python.python"] }}`, and the other installs the extension with `Install VS Code Extension` after the start. Both open `hello.py`, run *Python: Run Python File in Terminal* and wait for `Hello World`. The suite needs network access and a Python interpreter, as its documentation says.
- `windows.robot`: opens a new window with `ControlOrMeta+Shift+N`, which avoids the palette, where *New Window* also matches *New Window with Profile*. It switches to the new page, checks the workbench there, closes it, and checks the first window.

### Screenshots

- **In the example:** the tests call `Take Screenshot    filename=<name>` at their important steps, so every run has the pictures in its log. The names are stable: `notification`, `quick-pick`, `webview`, `editor`, `terminal` and `python-run`. The palette itself is not shown, because `Run Command` presses Enter at once; for the quick pick, `quick_pick.resource` gets `Quick Pick Item Should Be Shown`, so that the screenshot is taken while the list is open.
- **Script:** `docs/scripts/update_screenshots.py` runs the example from the repository root. It uses the example's `xvfb` profile, so the run is hidden on a Full HD screen with Openbox, where the maximised VS Code fills the screen. It then copies the selected screenshots from the run's `browser/screenshot` folder to `docs/src/assets/screenshots/`.
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
- `getting-started/vscode.md`: the `command-palette` screenshot.

## Risks / Trade-offs

- [VS Code registers an extension installed into a running instance shortly after the install, and an open command palette does not refresh] → `Run Command` opens a fresh palette until the command appears, see above.
- [`Install VS Code Extension` with `ms-python.python` needs a reload because of its dependencies] → Checked: VS Code 1.141 picks up the Python extension and its dependencies in the running instance without a reload.
- [The Python tests download about 100 MB from the Marketplace per instance] → Accepted for the example. The guide mentions it, and the tests are tagged `network` so that offline runs can exclude them.
- [Screenshots in the repository go stale] → The script makes regenerating one command, and AGENTS.md names when to run it. Stale pictures do not break anything.
- [The terminal shows personal shell output despite `sh`, for example through `ENV`] → It is checked when the screenshots are generated; the setting can name `/bin/sh` with arguments if needed.
