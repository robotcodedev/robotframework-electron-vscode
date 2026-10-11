# Spec Delta

## ADDED Requirements

### Requirement: Given extensions directory
`Open VS Code` SHALL accept an extensions directory and SHALL use it for the instance instead of an empty directory of its own. `extensions` SHALL be installed into that directory. The instance's user-data directory SHALL stay its own.

#### Scenario: Prepared extensions
- **WHEN** `Open VS Code` is called with `extensions_dir` pointing to a directory that holds an installed extension
- **THEN** the instance starts with that extension, and nothing is downloaded for it

#### Scenario: Without extensions_dir
- **WHEN** `Open VS Code` is called without `extensions_dir`
- **THEN** the instance uses an empty extensions directory of its own, as before

### Requirement: Instance directories
`Get VS Code Instance Directories` SHALL return the root, user-data and extensions directories of an instance that `Open VS Code` started, the active one or the one with a given browser id. It SHALL fail for a browser that `Open VS Code` did not start or that has been closed.

#### Scenario: Directories of the active instance
- **WHEN** `Get VS Code Instance Directories` is called after `Open VS Code`
- **THEN** it returns the directories that the instance uses, including a given `extensions_dir`

#### Scenario: Not an instance of Open VS Code
- **WHEN** `Get VS Code Instance Directories` is called for a browser that `Open VS Code` did not start
- **THEN** it fails with a message that names the browser

## REMOVED Requirements

### Requirement: Install extensions into a running instance
**Reason**: `Install VS Code Extension` only ran VS Code's command-line script with the instance's directories. `Run VS Code CLI` and `Get VS Code Instance Directories` do that now, for every use of the script. Waiting until the running instance has noticed the extension, which the keyword never did, is shown as a recipe in the guide on extensions.
**Migration**: Get the directories with `Get VS Code Instance Directories`, install with `Run VS Code CLI    ${dirs.extensions}    ${dirs.user_data}    --install-extension    <extension>`, and wait for the instance's report as the recipe "into a running instance" shows.
