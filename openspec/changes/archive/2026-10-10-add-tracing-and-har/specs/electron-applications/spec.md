# Spec Delta

## ADDED Requirements

### Requirement: Tracing
`New Electron Application` SHALL record a Playwright trace of the application when it is given `tracing`, with the values and paths of `tracing` of Browser's `New Context`, and also when the variable or environment variable `ROBOT_FRAMEWORK_BROWSER_TRACING` is `True`. The trace SHALL be saved when the application closes and SHALL show the keyword calls as groups.

#### Scenario: Trace of an application
- **WHEN** a test starts an application with `tracing` set to a `.zip` path, clicks in its window and closes it
- **THEN** the trace file exists, contains the click, and has a group for the `Click` keyword

#### Scenario: Tracing from the global setting
- **WHEN** `ROBOT_FRAMEWORK_BROWSER_TRACING` is `True` and a test starts and closes an application without `tracing`
- **THEN** a trace named after the application's context is in Browser's trace folder

#### Scenario: No tracing by default
- **WHEN** a test starts and closes an application without `tracing` and without the global setting
- **THEN** no trace is saved

### Requirement: HAR recording
`New Electron Application` SHALL record the network traffic of the application's windows into a HAR file when it is given `record_har`, with the keys of `recordHar` of Browser's `New Context`. A relative path SHALL be relative to the output directory. The file SHALL be written when the application closes.

#### Scenario: HAR of an application
- **WHEN** a test starts an application with `record_har`, loads a page from a web server in its window, makes the page fetch a resource and closes the application
- **THEN** the HAR file contains the request for the resource and its response

### Requirement: Downloads
Browser's `Download` SHALL work in an application's windows. The library SHALL give Browser the context options of the application, so that Browser knows that the application accepts downloads, as Electron does by default.

#### Scenario: Download in an application
- **WHEN** a window of an application shows a page from a web server and a test calls `Download` for a URL of that server
- **THEN** the file is saved with the content that the server returned
