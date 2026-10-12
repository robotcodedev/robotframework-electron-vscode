# vscode-launch Specification

## Purpose

Opens VS Code instances for end-to-end tests that are isolated from the user's own VS Code and from each other, with the extension under test loaded from source, and closes them again.

## Requirements

### Requirement: Keywords of Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and with it the Browser keywords that `Electron` provides, with Browser's import arguments, in addition to its own keywords. It SHALL hide the same Browser keywords as `Electron`. It SHALL add no import arguments of its own. Importing it, generating its documentation or analysing it in an editor SHALL NOT download VS Code, start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `New Electron Application` and `Switch Electron Application` can be called without a library prefix, and `New Context` cannot

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no download and no process start takes place

### Requirement: Open VS Code
`Open VS Code` SHALL start VS Code from a given version (as for `Get VS Code Executable`, default `stable`) or from a given executable path, which can also be a command on `PATH` or a symbolic link. It SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `New Electron Application`. If the workbench does not become ready, it SHALL fail with the error of that, close the instance, and leave no VS Code process running.

#### Scenario: Workbench is ready
- **WHEN** `Open VS Code` returns
- **THEN** the workbench window is the active page and Browser keywords act on it

#### Scenario: Local installation
- **WHEN** `Open VS Code` is called with the executable path of an installed VS Code
- **THEN** that installation is started and nothing is downloaded

#### Scenario: Executable behind a symbolic link
- **WHEN** `Open VS Code` is called with a symbolic link to a VS Code executable
- **THEN** the VS Code that the link points to starts

#### Scenario: Workbench does not become ready
- **WHEN** the workbench does not become ready within the time allowed
- **THEN** the keyword fails with the error of the wait, even if closing the instance fails as well, and no VS Code process of the instance is running

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
`Close VS Code` SHALL end the active instance, all instances, or the instance whose id is given, with the same behaviour as `Close Electron Application`.

#### Scenario: Instance ends
- **WHEN** `Close VS Code` is called
- **THEN** the VS Code process of the instance has exited when the keyword returns

### Requirement: VS Code forks
`Open VS Code` SHALL start VS Code forks, such as VSCodium, that are given as executable. Given the same executable, `Execute VS Code CLI Command` SHALL install extensions for them with the fork's own command-line script, and so from the fork's own extension gallery.

#### Scenario: VSCodium
- **WHEN** `Open VS Code` is called with the executable of VSCodium
- **THEN** the workbench is ready and Browser keywords act on it

#### Scenario: Extensions for a fork
- **WHEN** `Execute VS Code CLI Command` is called with the executable of VSCodium and `--install-extension`
- **THEN** the extension is installed with VSCodium's command-line script, from VSCodium's extension gallery

### Requirement: Earlier runs' instance directories are removed
When a test run starts, the library SHALL remove the instance directories that earlier runs left in the run's output directory, before the run opens its first instance. Instance directories of the current run SHALL be kept.

#### Scenario: New run in a used output directory
- **WHEN** a run starts in an output directory that holds instance directories from an earlier run
- **THEN** those directories are removed, and the first instance of the new run gets the number 1

#### Scenario: Instances of the same run
- **WHEN** two suites of one run each open VS Code
- **THEN** the instance directories of both suites are still there at the end of the run

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

### Requirement: Library documentation
The library documentation SHALL be the `VSCode` library's own: an introduction about opening VS Code, its instances, the workbench, extensions, closing, recording and the helper library, and import documentation with a link to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation, as in `Electron`.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction consists of the `VSCode` library's own text, its section `Assertions` links to the Browser library's documentation, and its section `Browser, Context and Page` compares the library with the Browser library

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation is the `VSCode` library's own text with a link to the Browser library's import arguments, and the import arguments are Browser's, with their types and defaults

### Requirement: Keyword documentation
The library's own keywords SHALL document every argument, their return value and the exceptions they raise for invalid input, so that Libdoc shows them with the arguments, the return type and the exceptions.

#### Scenario: Keyword documentation
- **WHEN** libdoc generates the documentation of `VSCode` or `VSCode.Helper`
- **THEN** every argument of their own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it

### Requirement: Given extensions directory
`Open VS Code` SHALL accept an extensions directory and SHALL use it for the instance instead of an empty directory of its own. The instance's user-data directory SHALL stay its own.

#### Scenario: Prepared extensions
- **WHEN** `Open VS Code` is called with `extensions_dir` pointing to a directory that holds an installed extension
- **THEN** the instance starts with that extension, and nothing is downloaded for it

#### Scenario: Without extensions_dir
- **WHEN** `Open VS Code` is called without `extensions_dir`
- **THEN** the instance uses an empty extensions directory of its own, as before

### Requirement: Instance directories
`Get VS Code Instance Directories` SHALL return the root, user-data and extensions directories of an instance that `Open VS Code` started, the active one or the one with a given id. It SHALL fail for an id that `Open VS Code` did not start or whose instance has been closed.

#### Scenario: Directories of the active instance
- **WHEN** `Get VS Code Instance Directories` is called after `Open VS Code`
- **THEN** it returns the directories that the instance uses, including a given `extensions_dir`

#### Scenario: Not an instance of Open VS Code
- **WHEN** `Get VS Code Instance Directories` is called with an id that `Open VS Code` did not return
- **THEN** it fails with a message that names the id

### Requirement: Launch options
`Open VS Code` SHALL accept `color_scheme`, `locale`, `timezone_id` and `bypass_csp` and start VS Code with them as `New Electron Application` does.

#### Scenario: Options reach the workbench
- **WHEN** a test opens VS Code with `color_scheme=dark`, `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** the workbench page matches `prefers-color-scheme: dark` and reports the language `pt-BR` and the time zone `Asia/Tokyo`

#### Scenario: Script added to the workbench
- **WHEN** a test opens VS Code with `bypass_csp=True` and adds a script element with inline code to the workbench through `Evaluate JavaScript`
- **THEN** the script runs, although the workbench requires Trusted Types for scripts

### Requirement: Main process of an instance
`Evaluate In Main Process` SHALL work for instances started by `Open VS Code`.

#### Scenario: VS Code's version from its main process
- **WHEN** a test opens VS Code 1.141.0 and evaluates `({ app }) => app.getVersion()` in its main process
- **THEN** the keyword returns `1.141.0`
