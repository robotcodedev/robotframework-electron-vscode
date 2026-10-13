# Spec Delta

## MODIFIED Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources. `Evaluate In Extension Host` gives access to VS Code's extension API and drives no part of the workbench.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Start VS Code`, `Close VS Code`, `Get VS Code Instance Directories`, `Execute VS Code CLI Command` and `Evaluate In Extension Host`

### Requirement: Examples run with the repository's tests
The examples SHALL run as part of the repository's tests, so that they keep working with the current libraries and VS Code.

#### Scenario: Example run
- **WHEN** the example's npm script has downloaded its VS Code, and `uv run robotcode -r examples/vscode-extension robot` runs from the repository root
- **THEN** all example tests pass

### Requirement: Self-contained template
The example SHALL be a self-contained extension project with its own `robot.toml` and `package.json`, which refer to nothing outside its folder, so that it can be copied as a starting point.

#### Scenario: Copied example
- **WHEN** the example folder is copied out of the repository, its npm script downloads VS Code, and it runs from its own root with the VSCode library installed
- **THEN** its tests pass

## ADDED Requirements

### Requirement: VS Code for the example
The example SHALL download the VS Code that it runs against with `@vscode/test-electron`, through an npm script in its `package.json`, into a folder of its own that git ignores. Its `robot.toml` SHALL point the variable `VSCODE_EXECUTABLE` to that VS Code, and a personal `.robot.toml` SHALL be able to point it to another one.

#### Scenario: Downloaded VS Code
- **WHEN** `npm ci` and the example's npm script run in the example's folder
- **THEN** VS Code 1.141.0 is in the example's folder, and the example's tests start it

#### Scenario: Another VS Code
- **WHEN** a personal `.robot.toml` sets `VSCODE_EXECUTABLE` to an installed VS Code
- **THEN** the example's tests start that VS Code
