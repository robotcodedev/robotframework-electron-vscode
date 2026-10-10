# vscode-launch Specification

## Purpose

Opens VS Code instances for end-to-end tests that are isolated from the user's own VS Code and from each other, with the extension under test loaded from source, and closes them again.

## Requirements

### Requirement: Drop-in replacement for Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and therefore every Browser keyword, with Browser's import arguments, in addition to its own keywords. It SHALL add no import arguments of its own. Importing it, generating its documentation or analysing it in an editor SHALL NOT download VS Code, start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `New Electron Application` can be called without a library prefix

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no download and no process start takes place

### Requirement: Open VS Code
`Open VS Code` SHALL start VS Code from a given version (as for `Get VS Code Executable`, default `stable`) or from a given executable path. It SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `New Electron Application`.

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

### Requirement: VS Code forks
`Open VS Code` SHALL start VS Code forks, such as VSCodium, that are given as executable. It SHALL install extensions for them with the fork's own command-line script, and so from the fork's own extension gallery.

#### Scenario: VSCodium
- **WHEN** `Open VS Code` is called with the executable of VSCodium
- **THEN** the workbench is ready and Browser keywords act on it

#### Scenario: Extensions for a fork
- **WHEN** `Open VS Code` is called with the executable of VSCodium and an extension identifier in `extensions`
- **THEN** the extension is installed into the instance with VSCodium's command-line script

### Requirement: Earlier runs' instance directories are removed
When a test run starts, the library SHALL remove the instance directories that earlier runs left in the run's output directory, before the run opens its first instance. Instance directories of the current run SHALL be kept.

#### Scenario: New run in a used output directory
- **WHEN** a run starts in an output directory that holds instance directories from an earlier run
- **THEN** those directories are removed, and the first instance of the new run gets the number 1

#### Scenario: Instances of the same run
- **WHEN** two suites of one run each open VS Code
- **THEN** the instance directories of both suites are still there at the end of the run

### Requirement: Install extensions into a running instance
`Install VS Code Extension` SHALL install a Marketplace extension or a `.vsix` file into a running instance that `Open VS Code` started, the active one or the one with a given browser id. It SHALL install the way `Open VS Code` installs its `extensions`, and SHALL return once the installation has finished.

#### Scenario: Extension in a running instance
- **WHEN** `Install VS Code Extension` installs a `.vsix` file into a running instance
- **THEN** the commands that the extension contributes become available in that instance without a restart

#### Scenario: Isolation
- **WHEN** `Install VS Code Extension` installs an extension into an instance
- **THEN** the extension is not installed in the user's own VS Code or in other instances

#### Scenario: Not an instance of Open VS Code
- **WHEN** `Install VS Code Extension` is called for a browser that `Open VS Code` did not start
- **THEN** it fails with a message that names the browser, and nothing is installed

### Requirement: Video recording
`Open VS Code` SHALL accept `record_video` and record the instance's windows as `New Electron Application` does.

#### Scenario: Video of a VS Code instance
- **WHEN** a test opens VS Code with `record_video`, runs a command and closes the instance
- **THEN** a video of the workbench exists at the path in the returned page details, and the log embeds it

### Requirement: Traces and HAR files
`Open VS Code` SHALL take `tracing` and `record_har` and pass them on to `New Electron Application`, so that it records a trace and a HAR file of the instance the same way.

#### Scenario: Trace and HAR of the workbench
- **WHEN** a test opens VS Code with `tracing` and `record_har` and closes it
- **THEN** both the trace file and the HAR file exist and are not empty
