# Spec Delta

## ADDED Requirements

### Requirement: Traces of tests
The example SHALL have a suite that records a Playwright trace of a test and a HAR file of a webview's network traffic. A guide on traces and HAR files SHALL include this suite from the example and explain how to open a trace.

#### Scenario: Traces of the example
- **WHEN** the example's tracing suite runs with `-p xvfb`
- **THEN** a trace of each test is in `browser/traces` of the output directory, and the HAR file of the webview test contains the webview's requests

#### Scenario: Guide on traces
- **WHEN** the documentation site is built
- **THEN** the guide on traces and HAR files shows the example's `tracing.robot` from `examples/vscode-extension`
