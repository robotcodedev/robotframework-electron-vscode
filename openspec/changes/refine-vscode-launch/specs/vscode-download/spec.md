# Spec Delta

## MODIFIED Requirements

### Requirement: Select a VS Code build
`Get VS Code Executable` in the `VSCode.Helper` library SHALL accept `stable`, `insiders` or a fixed version such as `1.95.0`, and SHALL return the path of the VS Code executable for the current platform. `stable` and `insiders` SHALL resolve to the newest build of that quality.

#### Scenario: Newest stable build
- **WHEN** `Get VS Code Executable    stable` is called
- **THEN** it returns the executable path of the newest stable VS Code for the current platform

#### Scenario: Fixed version
- **WHEN** `Get VS Code Executable    1.95.0` is called
- **THEN** it returns the executable path of VS Code 1.95.0

#### Scenario: Unknown version
- **WHEN** a version is requested that does not exist
- **THEN** the keyword fails with an error that names the version

### Requirement: Cache builds
A downloaded build SHALL be kept in a cache directory and reused by later calls in any run. The cache directory SHALL default to the user's cache directory and SHALL be configurable per call.

#### Scenario: Second call uses the cache
- **WHEN** the same version is requested a second time
- **THEN** no download takes place and the same executable path is returned

#### Scenario: Custom cache directory
- **WHEN** `Get VS Code Executable` is called with a cache directory
- **THEN** builds are stored in and read from that directory

### Requirement: Supported platforms
Downloads SHALL work on Linux (x64, arm64), Windows (x64) and macOS (x64, arm64).

#### Scenario: Linux
- **WHEN** `Get VS Code Executable    stable` runs on Linux x64
- **THEN** the returned path is an executable VS Code binary

## ADDED Requirements

### Requirement: Local executable
If an executable is given, `Get VS Code Executable` SHALL return it unchanged and SHALL NOT download anything.

#### Scenario: Installed VS Code
- **WHEN** the keyword is called with the executable of an installed VS Code
- **THEN** it returns that path without any network access

### Requirement: Independent of Browser state
Importing `VSCode.Helper` and calling its keywords SHALL NOT start the Playwright process or require an open browser.

#### Scenario: Helper without a browser
- **WHEN** a suite imports only `VSCode.Helper` and calls `Get VS Code Executable`
- **THEN** the keyword works and no Node.js process is started
