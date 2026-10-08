# Spec Delta

## Purpose

Opens VS Code instances for end-to-end tests that are isolated from the user's own VS Code and from each other, with the extension under test loaded from source, and closes them again.

## ADDED Requirements

### Requirement: Drop-in replacement for Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and therefore every Browser keyword, with Browser's import arguments, in addition to its own keywords. It SHALL add no import arguments of its own. Importing it, generating its documentation or analysing it in an editor SHALL NOT download VS Code, start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `New Electron Application` can be called without a library prefix

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no download and no process start takes place

### Requirement: Open VS Code
`Open VS Code` SHALL start VS Code from a given version (as for `Download VS Code`, default `stable`) or from a given executable path. It SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `New Electron Application`.

#### Scenario: Workbench is ready
- **WHEN** `Open VS Code` returns
- **THEN** the workbench window is the active page and Browser keywords act on it

#### Scenario: Local installation
- **WHEN** `Open VS Code` is called with the executable path of an installed VS Code
- **THEN** that installation is started and nothing is downloaded

### Requirement: Isolated instances
Each instance SHALL use its own user-data and extensions directories, so that neither the user's own VS Code settings and extensions nor other instances affect it. Environment variables starting with `VSCODE_` SHALL be removed from the environment the instance sees.

#### Scenario: User's VS Code is unaffected
- **WHEN** an instance is opened on a machine where the user's own VS Code is running
- **THEN** the instance starts as a separate application, and the user's settings and extensions are not visible in it

#### Scenario: Two instances
- **WHEN** a test opens two instances
- **THEN** both run at the same time, and closing one leaves the other open

### Requirement: Extension under test
`Open VS Code` SHALL load one or more extensions from source folders as development extensions.

#### Scenario: Development extension is active
- **WHEN** `Open VS Code` is called with the folder of an extension
- **THEN** the commands that the extension contributes are available in the command palette

### Requirement: Dependency extensions
`Open VS Code` SHALL install given extensions, as Marketplace identifiers or `.vsix` files, into the instance's extensions directory before it starts.

#### Scenario: Marketplace extension
- **WHEN** `Open VS Code` is called with the identifier of a Marketplace extension
- **THEN** that extension is installed in the instance and is not installed in the user's own VS Code

### Requirement: Settings
`Open VS Code` SHALL write given settings into the instance's user settings before it starts. By default, the instance SHALL start without welcome page, release notes, update checks, telemetry or workspace trust prompts. Given settings SHALL override these defaults.

#### Scenario: Setting takes effect
- **WHEN** `Open VS Code` is called with the setting `window.title` set to `robot-test`
- **THEN** `Get Title` returns `robot-test`

#### Scenario: Quiet start
- **WHEN** `Open VS Code` is called without settings
- **THEN** neither a welcome page nor a workspace trust prompt is shown

### Requirement: Open a folder or file
`Open VS Code` SHALL open a given folder as workspace, or a given file in an editor.

#### Scenario: Folder
- **WHEN** `Open VS Code` is called with a folder
- **THEN** the folder is open as workspace in the window

### Requirement: Logs are kept
The instance directories, including VS Code's logs, SHALL be created under the output directory of the run and kept after the instance closes.

#### Scenario: Logs after a failed test
- **WHEN** a test fails after opening VS Code
- **THEN** the VS Code logs of that instance can be found under the run's output directory

### Requirement: Close VS Code
`Close VS Code` SHALL end the active instance, or the instance whose browser id is given, with the same behaviour as `Close Electron Application`.

#### Scenario: Instance ends
- **WHEN** `Close VS Code` is called
- **THEN** the VS Code process of the instance has exited when the keyword returns
