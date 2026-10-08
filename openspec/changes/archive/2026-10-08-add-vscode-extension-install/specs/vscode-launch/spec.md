# Spec Delta

## ADDED Requirements

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
