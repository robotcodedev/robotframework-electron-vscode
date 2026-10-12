# Spec Delta

## Purpose

Lets tests of VS Code extensions use VS Code's extension API to prepare a test and to wait for a state. The code runs in the extension host of a window of an instance that `Open VS Code` started.

## ADDED Requirements

### Requirement: Evaluate in the extension host
`Evaluate In Extension Host` SHALL run a JavaScript function in an extension host of the active instance that `Open VS Code` started. The function SHALL be a required argument; further arguments continue it. It SHALL get the `vscode` module and the keyword's `arg`. The keyword SHALL wait for a returned promise and return the function's result.

#### Scenario: VS Code's version from the extension host
- **WHEN** a test opens VS Code 1.141.0 and evaluates `(vscode) => vscode.version` in the extension host
- **THEN** the keyword returns `1.141.0`

#### Scenario: Command by its id
- **WHEN** a test evaluates a function that executes a command of the test extension by its id
- **THEN** the command runs, and its notification appears in the workbench

#### Scenario: Function over several lines with an argument
- **WHEN** a test passes a function over several arguments and a dictionary as `arg`, and the function returns a value from it
- **THEN** the keyword returns that value

#### Scenario: Text of the active editor
- **WHEN** a test opens a file of the workspace and evaluates a function that returns the text of the active editor
- **THEN** the keyword returns the file's text

### Requirement: Failures of the evaluation
`Evaluate In Extension Host` SHALL fail with the function's error message when the function throws or its promise rejects. It SHALL fail when the result cannot be serialised as JSON, and when the evaluation does not finish within the library's timeout.

#### Scenario: Function throws
- **WHEN** a test evaluates a function that throws an error with the message `broken`
- **THEN** the keyword fails, and its message contains `broken`

#### Scenario: Evaluation does not finish
- **WHEN** a test sets the library's timeout to a few seconds and evaluates a function whose promise never settles
- **THEN** the keyword fails after the timeout

### Requirement: No VS Code instance
`Evaluate In Extension Host` SHALL fail with a message that says so when no instance is open, or when the active application was not started by `Open VS Code`.

#### Scenario: Application that is not a VS Code instance
- **WHEN** the active application was started by `New Electron Application` and a test evaluates a function in the extension host
- **THEN** the keyword fails with a message that the application is not a VS Code instance started by `Open VS Code`

### Requirement: Helper extension
`Open VS Code` SHALL load the library's helper extension as an additional development extension, next to the extensions under test. The helper SHALL accept evaluations only on `127.0.0.1` and only with a token. It SHALL write the token into the instance's user-data directory.

#### Scenario: Next to the extension under test
- **WHEN** a test opens VS Code with the test extension as `extension_development_path`
- **THEN** the commands of the test extension are available, and `Evaluate In Extension Host` works

#### Scenario: Without an extension under test
- **WHEN** a test opens VS Code without `extension_development_path`
- **THEN** `Evaluate In Extension Host` works

#### Scenario: Request without the token
- **WHEN** a client sends a request to the helper without the token
- **THEN** the helper rejects it and runs nothing

### Requirement: Switching the helper off
The `VSCode` library SHALL take the import argument `enable_extension_host_evaluation`, `True` by default. With `False`, `Open VS Code` SHALL NOT load the helper extension. `Evaluate In Extension Host` SHALL then fail with a message that names the import argument.

#### Scenario: Helper switched off
- **WHEN** a suite imports `VSCode` with `enable_extension_host_evaluation=False` and opens VS Code without `extension_development_path`
- **THEN** the window title does not start with `[Extension Development Host]`, and `Evaluate In Extension Host` fails with a message that names `enable_extension_host_evaluation`

### Requirement: Waiting for the extension host
`Evaluate In Extension Host` SHALL wait, up to the library's timeout, until the helper in the selected window's extension host accepts evaluations. This covers the start of the instance and a new extension host after the window reloads. It SHALL ignore extension hosts that have ended.

#### Scenario: Right after the start
- **WHEN** a test evaluates a function in the extension host directly after `Open VS Code`
- **THEN** the keyword returns the function's result

#### Scenario: After the window reloads
- **WHEN** a test reloads the workbench window and then evaluates a function in the extension host
- **THEN** the keyword returns the result from the new extension host

### Requirement: Choice of the window
Each workbench window has its own extension host. Windows into which editors are moved belong to their workbench window. `workspace` SHALL select the window that has the given folder or `.code-workspace` file open as its workspace. Without `workspace`, the keyword SHALL take the only extension host. If there are several, it SHALL take the one of the workbench window that shows the active page.

#### Scenario: Window by its workspace
- **WHEN** an instance has a window with folder `a` and a window with folder `b`, the window with `a` shows the active page, and a test evaluates with `workspace` set to folder `b`
- **THEN** the function runs in the extension host of the window with folder `b`

#### Scenario: Window of the active page
- **WHEN** an instance has two workbench windows and a test switches to the second one with `Switch Page`, then evaluates without `workspace`
- **THEN** the function runs in the extension host of the second window

#### Scenario: Editor moved into its own window
- **WHEN** a test moves an editor into a new window, switches to that window's page and evaluates without `workspace`
- **THEN** the function runs in the extension host of the workbench window that the editor came from

#### Scenario: Workspace that no window has open
- **WHEN** a test evaluates with a `workspace` that no window of the instance has open
- **THEN** the keyword fails after the library's timeout with a message that names the workspace and the open workspaces

#### Scenario: Several windows without a workspace
- **WHEN** an instance has two windows without a workspace, and a test evaluates without `workspace` on the page of one of them
- **THEN** the keyword fails with a message that the window cannot be determined
