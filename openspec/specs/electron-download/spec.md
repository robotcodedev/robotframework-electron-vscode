# electron-download Specification

## Purpose

Provides Electron binaries for tests: a given Electron release is downloaded once for the current platform, verified, cached, and reused afterwards.

## Requirements

### Requirement: Provide an Electron binary of a given version
`Get Electron Executable` in the `Electron.Helper` library SHALL return the path of the Electron executable of the given version for the current platform. It SHALL fail with an error that names the version if that release does not exist.

#### Scenario: Known version
- **WHEN** `Get Electron Executable    44.7.0` is called
- **THEN** it returns the path of an executable Electron 44.7.0 binary for the current platform

#### Scenario: Unknown version
- **WHEN** `Get Electron Executable    0.0.1` is called
- **THEN** the keyword fails with an error that names `0.0.1`

### Requirement: Cache downloads
A downloaded release SHALL be kept in a cache directory and reused by later calls in any run. The cache directory SHALL default to the user's cache directory, and SHALL be configurable per call.

#### Scenario: Second call uses the cache
- **WHEN** the same version is requested a second time
- **THEN** nothing is downloaded and the same path is returned

#### Scenario: Custom cache directory
- **WHEN** the keyword is called with a cache directory
- **THEN** the release is stored in and read from that directory

### Requirement: Only verified, complete downloads are used
A download SHALL be verified against the SHA-256 checksum the release publishes. A download that fails the check, or that was interrupted, SHALL never be used and SHALL leave nothing in the cache.

#### Scenario: Checksum mismatch
- **WHEN** the downloaded archive does not match the published checksum
- **THEN** the keyword fails and the cache does not contain that version

### Requirement: Local executable
If an executable is given, `Get Electron Executable` SHALL return it unchanged and SHALL NOT download anything.

#### Scenario: Locally installed Electron
- **WHEN** the keyword is called with an executable path
- **THEN** it returns that path without any network access

### Requirement: Independent of Browser state
Importing `Electron.Helper` and calling its keywords SHALL NOT start the Playwright process or require an open browser.

#### Scenario: Helper without a browser
- **WHEN** a suite imports only `Electron.Helper` and calls `Get Electron Executable`
- **THEN** the keyword works and no Node.js process is started

### Requirement: Supported platforms
Downloads SHALL work on Linux (x64, arm64), Windows (x64) and macOS (x64, arm64).

#### Scenario: Linux
- **WHEN** `Get Electron Executable    44.7.0` runs on Linux x64
- **THEN** the returned path is an executable Electron binary
