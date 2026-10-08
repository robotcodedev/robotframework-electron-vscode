# vscode-download Specification

## Purpose

Provides VS Code builds for tests. It resolves a requested version or quality, downloads the build once per platform and reuses the cached copy afterwards.

## Requirements

### Requirement: Select a VS Code build
`Download VS Code` SHALL accept `stable`, `insiders` or a fixed version such as `1.95.0`, and SHALL return the path of the VS Code executable for the current platform. `stable` and `insiders` SHALL resolve to the newest build of that quality.

#### Scenario: Newest stable build
- **WHEN** `Download VS Code    stable` is called
- **THEN** it returns the executable path of the newest stable VS Code for the current platform

#### Scenario: Fixed version
- **WHEN** `Download VS Code    1.95.0` is called
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
- **WHEN** `Download VS Code` is called with a cache directory
- **THEN** builds are stored in and read from that directory

### Requirement: Only complete builds are used
An interrupted, incomplete or corrupted download SHALL never be used. Every download SHALL be verified against the SHA-256 checksum that the update service publishes for the build. Parallel test processes that request the same uncached build SHALL all get the same executable path.

#### Scenario: Interrupted download
- **WHEN** a download was interrupted in an earlier run
- **THEN** the next call downloads the build again instead of using the partial files

#### Scenario: Checksum mismatch
- **WHEN** the downloaded archive does not match the published checksum
- **THEN** the keyword fails and the cache does not contain that build

#### Scenario: Parallel requests
- **WHEN** two test processes request the same uncached build at the same time
- **THEN** both get the same executable path, and the cache holds one complete copy of the build

### Requirement: Supported platforms
Downloads SHALL work on Linux (x64, arm64), Windows (x64) and macOS (x64, arm64).

#### Scenario: Linux
- **WHEN** `Download VS Code    stable` runs on Linux x64
- **THEN** the returned path is an executable VS Code binary
