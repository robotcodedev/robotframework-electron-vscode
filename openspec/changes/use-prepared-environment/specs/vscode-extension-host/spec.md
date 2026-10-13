# Spec Delta

## MODIFIED Requirements

### Requirement: Evaluate in the extension host
`Evaluate In Extension Host` SHALL run a JavaScript function in an extension host of the active instance that `Start VS Code` started, through the library's helper extension. The function SHALL be a required argument; further arguments continue it. It SHALL get the `vscode` module and the keyword's `arg`. The keyword SHALL wait for a returned promise and return the function's result.

#### Scenario: VS Code's version from the extension host
- **WHEN** a test starts VS Code 1.141.0 with the helper extension and evaluates `(vscode) => vscode.version` in the extension host
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

### Requirement: No VS Code instance
`Evaluate In Extension Host` SHALL fail with a message that says so when no instance is open, or when the active application was not started by `Start VS Code`.

#### Scenario: Application that is not a VS Code instance
- **WHEN** the active application was started by `Start Electron Application` and a test evaluates a function in the extension host
- **THEN** the keyword fails with a message that the application is not a VS Code instance started by `Start VS Code`

### Requirement: Waiting for the extension host
`Evaluate In Extension Host` SHALL wait, up to the library's timeout, until the helper in the selected window's extension host accepts evaluations. This covers the start of the instance and a new extension host after the window reloads. It SHALL ignore extension hosts that have ended.

#### Scenario: Right after the start
- **WHEN** a test evaluates a function in the extension host directly after `Start VS Code`
- **THEN** the keyword returns the function's result

#### Scenario: After the window reloads
- **WHEN** a test reloads the workbench window and then evaluates a function in the extension host
- **THEN** the keyword returns the result from the new extension host
