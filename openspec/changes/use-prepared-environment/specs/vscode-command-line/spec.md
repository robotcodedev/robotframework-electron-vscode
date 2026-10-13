# Spec Delta

## REMOVED Requirements

### Requirement: Run the command-line script
**Reason**: The keyword moves into the `VSCode` library and no longer selects a build by version. "Command-line script of the active instance" and "Command-line script of a given environment" replace this requirement.
**Migration**: Import `VSCode` instead of `VSCode.Helper`. Pass `executable` instead of `version` and `cache_dir`, or call the keyword without them on the running instance.

### Requirement: Explicit directories
**Reason**: The directories are no longer required. The keyword works on the directories of the active instance, or on the given environment with fresh directories for those that are not given, so the user's own VS Code stays unaffected either way.
**Migration**: Pass the directories as `extensions_dir` and `user_data_dir` after the script's arguments, together with `executable`.

## MODIFIED Requirements

### Requirement: Clean environment
`Execute VS Code CLI Command` SHALL run the script without the environment variables that start with `VSCODE_` and without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Run from VS Code's terminal
- **WHEN** `Execute VS Code CLI Command` runs in a test run started from VS Code's integrated terminal
- **THEN** the script works on the directories of the active instance or on the given ones, and does not contact the VS Code that the terminal belongs to

### Requirement: Usable without a browser
`Execute VS Code CLI Command` SHALL NOT start the Playwright process or require an open browser.

#### Scenario: Prepare before any browser
- **WHEN** a suite setup calls `Execute VS Code CLI Command` with an executable before any VS Code or browser is opened
- **THEN** the keyword works and no Node.js process is started

## ADDED Requirements

### Requirement: Command-line script of the active instance
Without `executable`, `user_data_dir` and `extensions_dir`, `Execute VS Code CLI Command` in the `VSCode` library SHALL run the command-line script of the active VS Code instance with the given arguments, on the instance's directories and with its environment, and SHALL return the script's output. Without an open instance, it SHALL fail with a message that names `executable`.

#### Scenario: Extensions of the running instance
- **WHEN** a test starts VS Code with a prepared extensions directory and calls `Execute VS Code CLI Command    --list-extensions`
- **THEN** the keyword returns the script's output, which names the prepared extension

#### Scenario: Install into the running instance
- **WHEN** a test calls `Execute VS Code CLI Command    --install-extension` with a `.vsix` after `Start VS Code`, without further arguments
- **THEN** the extension is in the instance's extensions directory

#### Scenario: No instance open
- **WHEN** no VS Code instance is open and a test calls `Execute VS Code CLI Command    --list-extensions`
- **THEN** the keyword fails with a message that no instance is open and that names `executable`

### Requirement: Command-line script of a given environment
With `executable`, `Execute VS Code CLI Command` SHALL run the command-line script of that VS Code on the environment that `Start VS Code` gets with the same `executable`, `user_data_dir` and `extensions_dir`: given directories as they are, the others fresh. `user_data_dir` or `extensions_dir` without `executable` SHALL fail.

#### Scenario: Install into a prepared directory
- **WHEN** a test installs an extension with `Execute VS Code CLI Command    --install-extension`, `executable` and `extensions_dir`, and then starts VS Code with the same `executable` and `extensions_dir`
- **THEN** the instance starts with the extension, and the user's own VS Code does not have it

#### Scenario: Directories without an executable
- **WHEN** a test calls `Execute VS Code CLI Command` with `extensions_dir` but without `executable`
- **THEN** the keyword fails with a message that names `executable`, and the script does not run

### Requirement: No window from the command-line script
`Execute VS Code CLI Command` SHALL fail without running the script when it gets no arguments for the script or an empty one, because VS Code's script then opens a VS Code window instead of running a command. On Linux, it SHALL run the script without `DISPLAY` and `WAYLAND_DISPLAY`, so that a call with `executable` but without a command of the script opens no window.

#### Scenario: Empty argument
- **WHEN** a test calls `Execute VS Code CLI Command    --install-extension    ${EMPTY}`
- **THEN** the keyword fails with a message about the empty argument, and the script does not run

#### Scenario: No arguments for the script
- **WHEN** a test calls `Execute VS Code CLI Command` with `executable` and without arguments for the script
- **THEN** the keyword fails with a message that the script needs arguments, and the script does not run

#### Scenario: No window on Linux
- **WHEN** a test on Linux calls `Execute VS Code CLI Command    --disable-extensions` with `executable`, which is no command of the script
- **THEN** no VS Code window opens, and no process of that VS Code is still running a few seconds later
