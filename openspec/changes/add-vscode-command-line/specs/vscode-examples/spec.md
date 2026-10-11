# Spec Delta

## MODIFIED Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Open VS Code`, `Close VS Code` and `Get VS Code Instance Directories`

### Requirement: Dependency extensions in the example
The example SHALL show a Marketplace extension that the extension under test depends on, `ms-python.python`, both prepared once with `Execute VS Code CLI Command` and copied into a VS Code before it starts, and installed into a running VS Code with `Execute VS Code CLI Command`, waiting until VS Code reports it.

#### Scenario: Installed at the start
- **WHEN** the example prepares `ms-python.python` once, opens VS Code with a copy of the prepared directory as `extensions_dir`, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

#### Scenario: Installed while running
- **WHEN** the example installs `ms-python.python` into a running instance with `Execute VS Code CLI Command`, waits until the instance's shared process log reports it, and runs `hello.py` with the Python extension's command
- **THEN** the terminal shows `Hello World`

### Requirement: Guides show the example
The documentation site SHALL have a guide on writing your own workbench keywords and locators, a guide on profiles per VS Code version and a guide on extensions, all of which include the example's files. The example SHALL keep the keywords and locators of each workbench part in a resource file of its own, so that a guide section shows a whole file.

#### Scenario: Guide on workbench keywords
- **WHEN** the documentation site is built
- **THEN** the guide on workbench keywords shows the example's resources for every workbench part, each from its file in `examples/vscode-extension`, and explains how to find locators with the RobotCode REPL

#### Scenario: Guide on VS Code versions
- **WHEN** the documentation site is built
- **THEN** the guide on profiles per VS Code version shows the example's `robot.toml` with its profile from `examples/vscode-extension`

#### Scenario: Guide on dependency extensions
- **WHEN** the documentation site is built
- **THEN** the guide on extensions shows the example's Python suite and its resource for extensions from `examples/vscode-extension`
