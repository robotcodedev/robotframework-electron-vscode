# Spec Delta

## ADDED Requirements

### Requirement: Video recording
`Open VS Code` SHALL accept `record_video` and record the instance's windows as `New Electron Application` does.

#### Scenario: Video of a VS Code instance
- **WHEN** a test opens VS Code with `record_video`, runs a command and closes the instance
- **THEN** a video of the workbench exists at the path in the returned page details, and the log embeds it
