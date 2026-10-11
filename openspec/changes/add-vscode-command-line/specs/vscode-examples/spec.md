# Spec Delta

## ADDED Requirements

### Requirement: Prepared extensions in the example
The example SHALL show the Python extension prepared once with `Run VS Code CLI` and used through a copy of the prepared directory for each VS Code it opens.

#### Scenario: Prepared before the start
- **WHEN** the example prepares `ms-python.python` once, opens VS Code with a copy of the prepared directory as `extensions_dir`, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

## MODIFIED Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Open VS Code`, `Close VS Code` and `Get VS Code Instance Directories`

### Requirement: Dependency extensions in the example
The example SHALL show a Marketplace extension that the extension under test depends on, `ms-python.python`, both installed when VS Code starts and installed into a running instance with `Run VS Code CLI`, waiting until the instance reports it.

#### Scenario: Installed at the start
- **WHEN** the example opens VS Code with `ms-python.python` in `extensions` and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

#### Scenario: Installed while running
- **WHEN** the example installs `ms-python.python` into a running instance with `Run VS Code CLI`, waits until the instance's shared process log reports it, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`
