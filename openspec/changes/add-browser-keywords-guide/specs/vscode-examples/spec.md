# Spec Delta

## MODIFIED Requirements

### Requirement: Guide on Browser features
The guide on Browser keywords in applications SHALL have a section on VS Code. It SHALL list the Browser features that need a setting in VS Code, and those that work differently in VS Code than in other Electron applications.

#### Scenario: A feature that does not work
- **WHEN** someone looks up `Save Page As PDF` in the guide
- **THEN** the guide says that it does not work with VS Code and why

#### Scenario: A feature that needs a setting
- **WHEN** someone looks up `Drag And Drop` in the explorer
- **THEN** the section on VS Code names the setting `explorer.confirmDragAndDrop`
