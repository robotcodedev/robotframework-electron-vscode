# Spec Delta

## MODIFIED Requirements

### Requirement: Install extensions into a running instance
`Install VS Code Extension` SHALL install a Marketplace extension or a `.vsix` file into a running instance that `Open VS Code` started, the active one or the one with a given browser id. It SHALL install the way `Open VS Code` installs its `extensions`, and SHALL return once the running instance has registered the extension.

#### Scenario: Extension in a running instance
- **WHEN** `Install VS Code Extension` installs a `.vsix` file into a running instance
- **THEN** the commands that the extension contributes become available in that instance without a restart

#### Scenario: Install right after the start
- **WHEN** `Install VS Code Extension` installs an extension while the instance is still starting, and the instance does not register it
- **THEN** the keyword uninstalls the extension and installs it again, and the instance registers it

#### Scenario: Concurrent write of the extension list
- **WHEN** the command-line script fails because the running instance writes `extensions.json` at the same time
- **THEN** the keyword runs the installation again

#### Scenario: Extension never registered
- **WHEN** the instance does not register the extension, even after it has been installed again
- **THEN** the keyword fails with an error that names the extension and the instance's shared process log

#### Scenario: Isolation
- **WHEN** `Install VS Code Extension` installs an extension into an instance
- **THEN** the extension is not installed in the user's own VS Code or in other instances

#### Scenario: Not an instance of Open VS Code
- **WHEN** `Install VS Code Extension` is called for a browser that `Open VS Code` did not start
- **THEN** it fails with a message that names the browser, and nothing is installed

#### Scenario: Closed instance
- **WHEN** `Install VS Code Extension` is called with the browser id of an instance that has been closed
- **THEN** it fails with a message that names the browser, and nothing is installed
