# Spec Delta

## MODIFIED Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources. `Evaluate In Extension Host` gives access to VS Code's extension API and drives no part of the workbench.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Open VS Code`, `Close VS Code`, `Get VS Code Instance Directories` and `Evaluate In Extension Host`

### Requirement: Dependency extensions in the example
The example SHALL show a Marketplace extension that the extension under test depends on, `ms-python.python`, both prepared once with `Execute VS Code CLI Command` and copied into a VS Code before it starts, and installed into a running VS Code with `Execute VS Code CLI Command`. The example's VS Code SHALL load the library's helper extension as a development extension next to the extension under test. For the running VS Code, the example SHALL wait for the extension host before the install and then until the extension host knows the extension; otherwise it SHALL install it again and reload the window.

#### Scenario: Installed at the start
- **WHEN** the example prepares `ms-python.python` once, opens VS Code with a copy of the prepared directory as `extensions_dir`, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

#### Scenario: Installed while running
- **WHEN** the example opens VS Code with the extension under test and the helper extension as development extensions, waits for the extension host, installs `ms-python.python` with `Execute VS Code CLI Command`, waits until `vscode.extensions.getExtension` finds it in the extension host, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`
