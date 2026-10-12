# Spec Delta

## MODIFIED Requirements

### Requirement: Keywords of Electron and Browser
The `VSCode` library SHALL provide every keyword of the `Electron` library, and with it the Browser keywords that `Electron` provides, in addition to its own keywords. It SHALL hide the same Browser keywords as `Electron`. Its import arguments SHALL be Browser's, followed by its own `enable_extension_host_evaluation`. Importing it, generating its documentation or analysing it in an editor SHALL NOT download VS Code, start the Playwright process or launch an application.

#### Scenario: Browser and Electron keywords
- **WHEN** a suite imports only `VSCode`
- **THEN** Browser keywords such as `Click` and Electron keywords such as `New Electron Application` and `Switch Electron Application` can be called without a library prefix, and `New Context` cannot

#### Scenario: Browser's import arguments
- **WHEN** a suite imports `VSCode` with `timeout=5s` and `enable_extension_host_evaluation=False`
- **THEN** the library's timeout is five seconds, and `Open VS Code` does not load the helper extension

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** it reports the version of `robotframework-vscode`, and no download and no process start takes place

### Requirement: Library documentation
The library documentation SHALL be the `VSCode` library's own: an introduction about opening VS Code, its instances, the workbench, extensions, the extension host, closing, recording and the helper library, and import documentation with a link to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation, as in `Electron`.

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the introduction consists of the `VSCode` library's own text, its section `Assertions` links to the Browser library's documentation, and its section `Browser, Context and Page` compares the library with the Browser library

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the import documentation is the `VSCode` library's own text with a link to the Browser library's import arguments and a description of `enable_extension_host_evaluation`, and the import arguments are Browser's, with their types and defaults, followed by `enable_extension_host_evaluation`
