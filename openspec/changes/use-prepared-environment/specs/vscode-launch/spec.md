# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Open VS Code`
- TO: `### Requirement: Start VS Code`

- FROM: `### Requirement: Given extensions directory`
- TO: `### Requirement: Given directories`

## MODIFIED Requirements

### Requirement: Keywords of Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and with it the Browser keywords that `Electron` provides, with Browser's import arguments, in addition to its own keywords. It SHALL hide the same Browser keywords as `Electron`. It SHALL add no import arguments of its own. Importing it, generating its documentation or analysing it in an editor SHALL NOT start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `Start Electron Application` and `Switch Electron Application` can be called without a library prefix, and `New Context` cannot

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no process start takes place

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

### Requirement: Isolated instances
Each instance SHALL use its own user-data and extensions directories, unless a test gives them, so that neither the user's own VS Code settings and extensions nor other instances affect it. Environment variables starting with `VSCODE_` SHALL be removed from the environment the instance sees.

#### Scenario: User's VS Code is unaffected
- **WHEN** an instance is started on a machine where the user's own VS Code is running
- **THEN** the instance starts as a separate application, and the user's settings and extensions are not visible in it

#### Scenario: Two instances
- **WHEN** a test starts two instances
- **THEN** both run at the same time, and closing one leaves the other open

### Requirement: Extension under test
`Start VS Code` SHALL load one or more extensions from source folders as development extensions.

#### Scenario: Development extension is active
- **WHEN** `Start VS Code` is called with the folder of an extension
- **THEN** the commands that the extension contributes are available in the command palette

### Requirement: Settings
`Start VS Code` SHALL write given settings into the user settings of a user-data directory that it creates, before VS Code starts. By default, the instance SHALL start without welcome page, release notes, update checks, telemetry or workspace trust prompts. Given settings SHALL override these defaults. The keyword SHALL write no settings into a given user-data directory, and SHALL fail when it gets both.

#### Scenario: Setting takes effect
- **WHEN** `Start VS Code` is called with the setting `window.title` set to `robot-test`
- **THEN** `Get Title` returns `robot-test`

#### Scenario: Quiet start
- **WHEN** `Start VS Code` is called without settings
- **THEN** neither a welcome page nor a workspace trust prompt is shown

#### Scenario: Settings with a given user-data directory
- **WHEN** `Start VS Code` is called with `user_data_dir` and `settings`
- **THEN** the keyword fails with a message that names both arguments, no process starts, and the user-data directory is unchanged

### Requirement: Open a folder or file
`Start VS Code` SHALL open a given folder as workspace, or a given file in an editor.

#### Scenario: Folder
- **WHEN** `Start VS Code` is called with a folder
- **THEN** the folder is open as workspace in the window

### Requirement: Logs are kept
The directories that the library creates for an instance, including VS Code's logs in a user-data directory that it creates, SHALL be created under the output directory of the run and kept after the instance closes. With a given user-data directory, VS Code's logs SHALL be in that directory.

#### Scenario: Logs after a failed test
- **WHEN** a test fails after starting VS Code without `user_data_dir`
- **THEN** the VS Code logs of that instance can be found under the run's output directory

### Requirement: VS Code forks
`Start VS Code` SHALL start VS Code forks, such as VSCodium, that are given as executable. Given the same executable, `Execute VS Code CLI Command` SHALL install extensions for them with the fork's own command-line script, and so from the fork's own extension gallery.

#### Scenario: VSCodium
- **WHEN** `Start VS Code` is called with the executable of VSCodium
- **THEN** the workbench is ready and Browser keywords act on it

#### Scenario: Extensions for a fork
- **WHEN** `Execute VS Code CLI Command` is called with the executable of VSCodium and `--install-extension`
- **THEN** the extension is installed with VSCodium's command-line script, from VSCodium's extension gallery

### Requirement: Video recording
`Start VS Code` SHALL accept `record_video` and record the instance's windows as `Start Electron Application` does.

#### Scenario: Video of a VS Code instance
- **WHEN** a test starts VS Code with `record_video`, runs a command and closes the instance
- **THEN** a video of the workbench exists at the path in the returned page details, and the log embeds it

### Requirement: Traces and HAR files
`Start VS Code` SHALL take `tracing` and `record_har` and pass them on to `Start Electron Application`, so that it records a trace and a HAR file of the instance the same way.

#### Scenario: Trace and HAR of the workbench
- **WHEN** a test starts VS Code with `tracing` and `record_har` and closes it
- **THEN** both the trace file and the HAR file exist and are not empty

### Requirement: Library documentation
The library documentation SHALL be the `VSCode` library's own: an introduction about starting VS Code, its instances and their directories, the workbench, extensions and the command-line script, the extension host, closing and recording, and import documentation with a link to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation, as in `Electron`.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction consists of the `VSCode` library's own text, its section `Assertions` links to the Browser library's documentation, and its section `Browser, Context and Page` compares the library with the Browser library

#### Scenario: The extension host
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction has a section `The extension host`, which names the helper extension's folder and `.vsix` in the package and how a test loads each

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation is the `VSCode` library's own text with a link to the Browser library's import arguments, and the import arguments are Browser's, with their types and defaults

### Requirement: Keyword documentation
The library's own keywords SHALL document every argument, their return value and the exceptions they raise for invalid input, so that Libdoc shows them with the arguments, the return type and the exceptions.

#### Scenario: Keyword documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** every argument of its own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it

### Requirement: Given directories
`Start VS Code` SHALL accept an extensions directory and a user-data directory, and SHALL use each given directory for the instance as it is, instead of a fresh one of its own. A directory that is not given SHALL be the instance's own, fresh one.

#### Scenario: Prepared extensions
- **WHEN** `Start VS Code` is called with `extensions_dir` pointing to a directory that holds an installed extension
- **THEN** the instance starts with that extension, and nothing is downloaded for it

#### Scenario: Prepared user data
- **WHEN** `Start VS Code` is called with `user_data_dir` pointing to a directory whose user settings set `window.title` to `prepared`
- **THEN** `Get Title` returns `prepared`, and the instance's extensions directory is a fresh one of its own

#### Scenario: Without extensions_dir
- **WHEN** `Start VS Code` is called without `extensions_dir`
- **THEN** the instance uses an empty extensions directory of its own, as before

### Requirement: Launch options
`Start VS Code` SHALL accept `color_scheme`, `locale`, `timezone_id` and `bypass_csp` and start VS Code with them as `Start Electron Application` does.

#### Scenario: Options reach the workbench
- **WHEN** a test starts VS Code with `color_scheme=dark`, `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** the workbench page matches `prefers-color-scheme: dark` and reports the language `pt-BR` and the time zone `Asia/Tokyo`

#### Scenario: Script added to the workbench
- **WHEN** a test starts VS Code with `bypass_csp=True` and adds a script element with inline code to the workbench through `Evaluate JavaScript`
- **THEN** the script runs, although the workbench requires Trusted Types for scripts

### Requirement: Main process of an instance
`Evaluate In Main Process` SHALL work for instances started by `Start VS Code`.

#### Scenario: VS Code's version from its main process
- **WHEN** a test starts VS Code 1.141.0 and evaluates `({ app }) => app.getVersion()` in its main process
- **THEN** the keyword returns `1.141.0`

## REMOVED Requirements

### Requirement: Instance directories
**Reason**: The keyword that starts an instance is now `Start VS Code`, and a scenario name holds the old name, which a MODIFIED block cannot change. "Directories of an instance" replaces the requirement, with the given user-data directory added.
**Migration**: None needed. `Get VS Code Instance Directories` keeps its name and arguments.

## ADDED Requirements

### Requirement: Directories of an instance
`Get VS Code Instance Directories` SHALL return the root, user-data and extensions directories of an instance that `Start VS Code` started, the active one or the one with a given id, including given directories. It SHALL fail for an id that `Start VS Code` did not start or whose instance has been closed.

#### Scenario: Directories of the active instance
- **WHEN** `Get VS Code Instance Directories` is called after `Start VS Code`
- **THEN** it returns the directories that the instance uses, including a given `extensions_dir` and `user_data_dir`

#### Scenario: Not an instance of Start VS Code
- **WHEN** `Get VS Code Instance Directories` is called with an id that `Start VS Code` did not return
- **THEN** it fails with a message that names the id
