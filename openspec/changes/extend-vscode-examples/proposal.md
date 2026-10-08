# Proposal

## Why

The example project shows four workbench parts: the command palette, quick picks, notifications and a webview. Real extension tests also open a project, edit files, read the terminal and depend on other extensions. The feature spike on 2026-10-08 tried all of this against VS Code 1.141 and found that it works with plain Browser keywords:
- Quick Open and the editor, saving files.
- The integrated terminal.
- VS Code's own file dialog, which `files.simpleDialog.enable` switches on.
- A second window as a new page.
- Locator handlers that close notifications.
- Screenshots, aria snapshots and the console log.
- `ms-python.python`, installed through `extensions`, ran a Python file in the terminal.

The documentation has no pictures yet, and it does not show how to find locators interactively with the RobotCode REPL.

## What Changes

- **Workspace:** the example gets a workspace with a small Python script. Every instance opens a fresh copy of it in the output directory, so tests can change files without touching the repository.
- **New resources and suites** in the example, each resource covering one workbench part as before:
  - editor: open a file through Quick Open, type, save;
  - file dialog: open a file through VS Code's own dialog;
  - terminal: read the terminal's output.
- **Python extension:**
  - one test installs `ms-python.python` with `extensions` of `Open VS Code`, and another installs it into the running instance with `Install VS Code Extension`;
  - both run `hello.py` with the Python extension's command and read `Hello World` in the terminal.
- **Second window:** a test opens one and switches to it as a new page.
- **Screenshots:**
  - the example's tests take screenshots at the important steps;
  - a script in `docs/` runs the example and copies selected screenshots into the site, where they are committed, like the reference pages.
- **Guides:**
  - the guide on workbench keywords covers the new resources and a section on finding locators with the RobotCode REPL;
  - a new guide shows which Browser features work in VS Code and which do not, with short snippets for those the example does not use, such as locator handlers, drag and drop and coverage;
  - a new guide covers dependency extensions;
  - the CI guide explains Xvfb's screen size.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-examples`: more workbench parts, a workspace copy per instance, dependency extensions, screenshots generated for the documentation, and more guides.

## Impact

- `examples/vscode-extension/`: workspace, resources, suites, `README.md`.
- `docs/`: guides, a screenshot script and the screenshots in `docs/src/assets/screenshots/`.
- `AGENTS.md`: the command that regenerates the screenshots.
- Depends on `add-vscode-extension-install` for `Install VS Code Extension`, which is applied first.
- The Python tests need network access for the Marketplace and a Python interpreter on the `PATH`.
