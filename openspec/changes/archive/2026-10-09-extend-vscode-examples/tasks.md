# Tasks

## 1. Example

- [x] 1.1 Add `tests/workspace/` (`hello.py`, a text file), `Example Workspace`, and the fresh copy and the settings in `Open Example VS Code`, which also passes on `&{options}`. Check the `sh` profile name with the RobotCode REPL. Verify that the existing example tests still pass.
- [x] 1.2 Write `editor.resource`, `file_dialog.resource` and `terminal.resource`, and the suites `editor.robot`, `terminal.robot` and `windows.robot` for the scenarios "Edit and save a file", "File dialog", "Terminal" and "Second window". Try the locators in the RobotCode REPL first. Verify that the example passes, and the scenario "Repository stays unchanged" with `git status`.
- [x] 1.3 Write `python.robot` for the scenarios "Installed at the start" and "Installed while running", tagged `network`. `Run Command` opens a fresh palette until the command appears. Verify that both pass. If the running install needs a reload, add it and note it in the design.
- [x] 1.4 Add `Take Screenshot` calls with stable names at the important steps of the example tests, and update the example's `README.md` (new suites, network and Python needs, `-e network`). Verify that a run produces the named screenshots, that `analyze code` reports no errors or warnings, and that the commands in the README run as written.

## 2. Documentation

- [x] 2.1 Write `docs/scripts/update_screenshots.py` and generate the screenshots into `docs/src/assets/screenshots/`. Add the command to `AGENTS.md`. Verify the scenario "Regenerate the screenshots": the script runs from a clean state, and the images come from a Full HD Xvfb screen, show the whole VS Code window and no personal shell prompt.
- [x] 2.2 Extend `workbench-keywords.mdx` with the new resources and the section on finding locators with the RobotCode REPL. Write `extensions.mdx` and `browser-features.md`, and update `getting-started/vscode.md`. Verify every snippet that is not included from the example in a RobotCode REPL session, and verify the scenarios "Guide on workbench keywords", "Guide on dependency extensions" and "A feature that does not work" with `npm run build`, with no broken links.
