## MODIFIED Requirements

### Requirement: Start VS Code
`Start VS Code` SHALL start VS Code from a given executable, which is required and can also be a command on `PATH` or a symbolic link. The library SHALL NOT download VS Code. The keyword SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `Start Electron Application`. If the workbench does not become ready, it SHALL fail with the error of that, close the instance, and leave no VS Code process running.

#### Scenario: Workbench is ready
- **WHEN** `Start VS Code` returns
- **THEN** the workbench window is the active page and Browser keywords act on it

#### Scenario: Local installation
- **WHEN** `Start VS Code` is called with the executable path of an installed VS Code
- **THEN** that installation is started and nothing is downloaded

#### Scenario: Executable behind a symbolic link
- **WHEN** `Start VS Code` is called with a symbolic link to a VS Code executable
- **THEN** the VS Code that the link points to starts

#### Scenario: Executable is required
- **WHEN** a test calls `Start VS Code` without an executable
- **THEN** Robot Framework, and RobotCode's analysis, report the missing argument, and no process starts

#### Scenario: Workbench does not become ready
- **WHEN** the workbench does not become ready within the time allowed
- **THEN** the keyword fails with the error of the wait, even if closing the instance fails as well, and no VS Code process of the instance is running

#### Scenario: VS Code does not start
- **WHEN** the executable ends before VS Code has answered
- **THEN** the keyword fails with an error that shows the output and the exit code of the executable, an application that was already open keeps working, and the next start works
