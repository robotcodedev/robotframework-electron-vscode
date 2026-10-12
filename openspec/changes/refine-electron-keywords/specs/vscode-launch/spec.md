# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Drop-in replacement for Electron and Browser`
- TO: `### Requirement: Keywords of Electron and Browser`

## MODIFIED Requirements

### Requirement: Keywords of Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and with it the Browser keywords that `Electron` provides, with Browser's import arguments, in addition to its own keywords. It SHALL hide the same Browser keywords as `Electron`. It SHALL add no import arguments of its own. Importing it, generating its documentation or analysing it in an editor SHALL NOT download VS Code, start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `New Electron Application` and `Switch Electron Application` can be called without a library prefix, and `New Context` cannot

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no download and no process start takes place

### Requirement: Close VS Code
`Close VS Code` SHALL end the active instance, all instances, or the instance whose id is given, with the same behaviour as `Close Electron Application`.

#### Scenario: Instance ends
- **WHEN** `Close VS Code` is called
- **THEN** the VS Code process of the instance has exited when the keyword returns

### Requirement: Library documentation
The library documentation SHALL be the `VSCode` library's own: an introduction about opening VS Code, its instances, the workbench, extensions, closing, recording and the helper library, and import documentation with a link to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation, as in `Electron`.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction consists of the `VSCode` library's own text, its section `Assertions` links to the Browser library's documentation, and its section `Browser, Context and Page` compares the library with the Browser library

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation is the `VSCode` library's own text with a link to the Browser library's import arguments, and the import arguments are Browser's, with their types and defaults

### Requirement: Instance directories
`Get VS Code Instance Directories` SHALL return the root, user-data and extensions directories of an instance that `Open VS Code` started, the active one or the one with a given id. It SHALL fail for an id that `Open VS Code` did not start or whose instance has been closed.

#### Scenario: Directories of the active instance
- **WHEN** `Get VS Code Instance Directories` is called after `Open VS Code`
- **THEN** it returns the directories that the instance uses, including a given `extensions_dir`

#### Scenario: Not an instance of Open VS Code
- **WHEN** `Get VS Code Instance Directories` is called with an id that `Open VS Code` did not return
- **THEN** it fails with a message that names the id
