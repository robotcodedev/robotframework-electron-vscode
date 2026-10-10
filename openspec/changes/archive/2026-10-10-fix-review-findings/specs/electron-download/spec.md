# Spec Delta

## MODIFIED Requirements

### Requirement: Only verified, complete downloads are used
A download SHALL be verified against the SHA-256 checksum the release publishes. A download that fails the check, that was interrupted, or whose archive contains an entry outside the release folder SHALL never be used and SHALL leave nothing in the cache. A download SHALL fail with an error instead of waiting forever when the server stops responding.

#### Scenario: Checksum mismatch
- **WHEN** the downloaded archive does not match the published checksum
- **THEN** the keyword fails and the cache does not contain that version

#### Scenario: Archive entry outside the release folder
- **WHEN** the archive contains an entry with an absolute path, a path that leaves the release folder, or a link that points outside it
- **THEN** the keyword fails, nothing is written outside the cache, and the cache does not contain that version

#### Scenario: Server stops responding
- **WHEN** the server accepts the connection but stops sending data
- **THEN** the keyword fails with an error after a timeout instead of waiting forever

### Requirement: Supported platforms
Downloads SHALL work on Linux (x64, arm64), Windows (x64) and macOS (x64, arm64). On other operating systems or processor architectures, the keyword SHALL fail with an error that names them, and nothing SHALL be downloaded.

#### Scenario: Linux
- **WHEN** `Get Electron Executable    44.7.0` runs on Linux x64
- **THEN** the returned path is an executable Electron binary

#### Scenario: Unsupported architecture
- **WHEN** `Get Electron Executable` runs on a processor architecture without Electron releases, such as 32-bit ARM
- **THEN** the keyword fails with an error that names the architecture, and nothing is downloaded
