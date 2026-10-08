# Spec Delta

## MODIFIED Requirements

### Requirement: Open VS Code
`Open VS Code` SHALL start VS Code from a given version (as for `Get VS Code Executable`, default `stable`) or from a given executable path. It SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `New Electron Application`.

#### Scenario: Workbench is ready
- **WHEN** `Open VS Code` returns
- **THEN** the workbench window is the active page and Browser keywords act on it

#### Scenario: Local installation
- **WHEN** `Open VS Code` is called with the executable path of an installed VS Code
- **THEN** that installation is started and nothing is downloaded

## ADDED Requirements

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
