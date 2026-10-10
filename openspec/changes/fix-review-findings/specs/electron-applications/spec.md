# Spec Delta

## MODIFIED Requirements

### Requirement: Start an application
`New Electron Application` SHALL start the Electron application at a given executable path, or a command on `PATH`, and SHALL return once the application's first window has opened. How long it waits for that window SHALL be configurable per call. Command-line arguments, a working directory and environment variables SHALL be passed to the application as given. A relative executable path and a relative working directory SHALL be relative to the test run's working directory, and without a working directory the application SHALL run in the test run's working directory. If no environment variables are given, the application SHALL inherit the environment of the test run without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Application opens a window
- **WHEN** `New Electron Application` is called with the path of an Electron application
- **THEN** the keyword returns after the application's first window has opened

#### Scenario: Arguments and environment
- **WHEN** the keyword is called with command-line arguments, a working directory and environment variables
- **THEN** the application receives these arguments, runs in that directory and sees exactly these environment variables

#### Scenario: Test run started from inside VS Code
- **WHEN** the test run has `ELECTRON_RUN_AS_NODE=1` in its environment, as runs started from VS Code do, and no environment variables are given
- **THEN** the application starts normally and does not see `ELECTRON_RUN_AS_NODE`

#### Scenario: Default working directory
- **WHEN** the keyword is called without a working directory
- **THEN** the application runs in the test run's working directory

#### Scenario: Relative executable path
- **WHEN** the keyword is called with an executable path relative to the test run's working directory
- **THEN** the application starts

#### Scenario: First window closes during the start
- **WHEN** the application's first window closes while the keyword takes the application over
- **THEN** the keyword returns without an error, and windows that the application opens later can be selected with `Switch Page`

### Requirement: Failed start
If the application cannot be started, opens no window within the time allowed, or cannot be taken over by the Browser library, `New Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state.

#### Scenario: Wrong executable path
- **WHEN** the executable path does not exist
- **THEN** the keyword fails with an error that names the path

#### Scenario: No window
- **WHEN** the application opens no window within the time allowed
- **THEN** the keyword fails, and afterwards no process of the application is running

#### Scenario: Browser cannot take the application over
- **WHEN** the Browser library cannot take over the started application, for example because it has no `adoptContext` hook
- **THEN** the keyword fails with an error that names the cause, and afterwards no process of the application is running
