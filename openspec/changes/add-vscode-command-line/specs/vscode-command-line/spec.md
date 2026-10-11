# Spec Delta

## Purpose

Run VS Code's command-line script, for example to install, uninstall or list extensions, against directories that the test gives explicitly, so that the user's own VS Code is never affected.

## ADDED Requirements

### Requirement: Run the command-line script
`Execute VS Code CLI Command` in `VSCode.Helper` SHALL run the command-line script of a VS Code build with the given arguments and SHALL return the script's output. The build SHALL be selected as for `Get VS Code Executable`, from a version or a given executable.

#### Scenario: List extensions
- **WHEN** `Execute VS Code CLI Command` is called with `--list-extensions` for an extensions directory that holds an extension
- **THEN** the keyword returns the output of the script, which names that extension

#### Scenario: Fixed version
- **WHEN** `Execute VS Code CLI Command` is called with `version=1.141.0`
- **THEN** the command-line script of VS Code 1.141.0 runs, downloaded and cached as for `Get VS Code Executable`

### Requirement: Explicit directories
`Execute VS Code CLI Command` SHALL require an extensions directory and a user-data directory and SHALL pass them to the script, so that a call never works on the user's own VS Code.

#### Scenario: Directories are required
- **WHEN** `Execute VS Code CLI Command` is called without an extensions directory or a user-data directory
- **THEN** Robot Framework reports the missing argument, and the script does not run

#### Scenario: Install into a prepared directory
- **WHEN** `Execute VS Code CLI Command` installs an extension with `--install-extension` into given directories
- **THEN** the extension is in the given extensions directory and not in the user's own VS Code

### Requirement: Clean environment
`Execute VS Code CLI Command` SHALL run the script without the environment variables that start with `VSCODE_` and without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Run from VS Code's terminal
- **WHEN** `Execute VS Code CLI Command` runs in a test run started from VS Code's integrated terminal
- **THEN** the script works on the given directories and does not contact the VS Code that the terminal belongs to

### Requirement: Failures
`Execute VS Code CLI Command` SHALL fail with the script's output if the script ends with an error, and SHALL fail if the script does not finish within a time limit.

#### Scenario: Unknown extension
- **WHEN** `Execute VS Code CLI Command` installs an extension that does not exist
- **THEN** the keyword fails with the script's message

### Requirement: Usable without a browser
`Execute VS Code CLI Command` SHALL NOT start the Playwright process or require an open browser.

#### Scenario: Prepare before any browser
- **WHEN** a suite setup calls `Execute VS Code CLI Command` before any VS Code or browser is opened
- **THEN** the keyword works and no Node.js process is started
