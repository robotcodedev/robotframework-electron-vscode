# Spec Delta

## ADDED Requirements

### Requirement: Main process of an instance
`Evaluate In Main Process` SHALL work for instances started by `Open VS Code`.

#### Scenario: VS Code's version from its main process
- **WHEN** a test opens VS Code 1.141.0 and evaluates `({ app }) => app.getVersion()` in its main process
- **THEN** the keyword returns `1.141.0`
