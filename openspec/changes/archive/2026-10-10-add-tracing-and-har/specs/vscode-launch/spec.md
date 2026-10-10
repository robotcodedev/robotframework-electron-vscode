# Spec Delta

## ADDED Requirements

### Requirement: Traces and HAR files
`Open VS Code` SHALL take `tracing` and `record_har` and pass them on to `New Electron Application`, so that it records a trace and a HAR file of the instance the same way.

#### Scenario: Trace and HAR of the workbench
- **WHEN** a test opens VS Code with `tracing` and `record_har` and closes it
- **THEN** both the trace file and the HAR file exist and are not empty
