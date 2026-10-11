# Spec Delta

## ADDED Requirements

### Requirement: Given extensions directory
`Open VS Code` SHALL accept an extensions directory and SHALL use it for the instance instead of an empty directory of its own. The instance's user-data directory SHALL stay its own.

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
- **WHEN** `Open VS Code` is called with a symbolic link to a VS Code executable
- **THEN** the VS Code that the link points to starts

#### Scenario: Workbench does not become ready
- **WHEN** the workbench does not become ready within the time allowed
- **THEN** the keyword fails with the error of the wait, even if closing the instance fails as well, and no VS Code process of the instance is running

### Requirement: VS Code forks
`Open VS Code` SHALL start VS Code forks, such as VSCodium, that are given as executable. Given the same executable, `Execute VS Code CLI Command` SHALL install extensions for them with the fork's own command-line script, and so from the fork's own extension gallery.

#### Scenario: VSCodium
- **WHEN** `Open VS Code` is called with the executable of VSCodium
- **THEN** the workbench is ready and Browser keywords act on it

#### Scenario: Extensions for a fork
- **WHEN** `Execute VS Code CLI Command` is called with the executable of VSCodium and `--install-extension`
- **THEN** the extension is installed with VSCodium's command-line script, from VSCodium's extension gallery

## REMOVED Requirements

### Requirement: Dependency extensions
**Reason**: Installing extensions is left to the tests. `Execute VS Code CLI Command` installs them into a directory that `Open VS Code` uses through `extensions_dir`, with every option of VS Code's command line, such as fixed versions and pre-releases.
**Migration**: Replace `extensions=${{ ["ms-python.python"] }}` with `Execute VS Code CLI Command    ${dir}/extensions    ${dir}/user-data    --install-extension    ms-python.python` and `Open VS Code    extensions_dir=${dir}/extensions`, as the guide on extensions shows.

### Requirement: Install extensions into a running instance
**Reason**: `Install VS Code Extension` only ran VS Code's command-line script with the instance's directories. `Execute VS Code CLI Command` and `Get VS Code Instance Directories` do that now, for every use of the script. Waiting until the running instance has noticed the extension, which the keyword never did, is shown as a recipe in the guide on extensions.
**Migration**: Get the directories with `Get VS Code Instance Directories`, install with `Execute VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    <extension>`, and wait for the instance's report as the recipe "into a running instance" shows.
