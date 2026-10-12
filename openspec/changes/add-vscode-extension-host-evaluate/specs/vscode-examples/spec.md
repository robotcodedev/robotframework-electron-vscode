# Spec Delta

## MODIFIED Requirements

### Requirement: No workbench keywords in the library
The `VSCode` library SHALL NOT provide keywords or locators for parts of the VS Code workbench, such as the command palette, quick picks, notifications or webviews. Projects define them in their own resources. `Evaluate In Extension Host` gives access to VS Code's extension API and drives no part of the workbench.

#### Scenario: Keywords of the library
- **WHEN** libdoc generates the documentation of `VSCode`
- **THEN** the only keywords it adds to those of `Electron` are `Open VS Code`, `Close VS Code`, `Get VS Code Instance Directories` and `Evaluate In Extension Host`
