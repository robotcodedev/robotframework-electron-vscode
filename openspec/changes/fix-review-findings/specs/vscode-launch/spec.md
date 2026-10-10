# Spec Delta

## MODIFIED Requirements

### Requirement: Open VS Code
`Open VS Code` SHALL start VS Code from a given version (as for `Get VS Code Executable`, default `stable`) or from a given executable path, which can also be a command on `PATH` or a symbolic link. It SHALL return once the workbench is ready for input, and its return value SHALL have the same form as that of `New Electron Application`. If the workbench does not become ready, it SHALL fail with the error of that, close the instance, and leave no VS Code process running.

#### Scenario: Workbench is ready
- **WHEN** `Open VS Code` returns
- **THEN** the workbench window is the active page and Browser keywords act on it

#### Scenario: Local installation
- **WHEN** `Open VS Code` is called with the executable path of an installed VS Code
- **THEN** that installation is started and nothing is downloaded

#### Scenario: Executable behind a symbolic link
- **WHEN** `Open VS Code` is called with a symbolic link to a VS Code executable and with `extensions`
- **THEN** VS Code starts, and the extensions are installed with the command-line script of that VS Code

#### Scenario: Workbench does not become ready
- **WHEN** the workbench does not become ready within the time allowed
- **THEN** the keyword fails with the error of the wait, even if closing the instance fails as well, and no VS Code process of the instance is running

### Requirement: Dependency extensions
`Open VS Code` SHALL install given extensions, as Marketplace identifiers or `.vsix` files, into the instance's extensions directory before it starts. An installation that does not finish within a time limit SHALL fail with an error instead of waiting forever.

#### Scenario: Marketplace extension
- **WHEN** `Open VS Code` is called with the identifier of a Marketplace extension
- **THEN** that extension is installed in the instance and is not installed in the user's own VS Code

#### Scenario: Installation does not finish
- **WHEN** the command-line script does not finish installing an extension within the time limit
- **THEN** the keyword fails with an error that names the extension

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

#### Scenario: Closed instance
- **WHEN** `Install VS Code Extension` is called with the browser id of an instance that has been closed
- **THEN** it fails with a message that names the browser, and nothing is installed
