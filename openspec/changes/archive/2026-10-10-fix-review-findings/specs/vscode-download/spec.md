# Spec Delta

## MODIFIED Requirements

### Requirement: Select a VS Code build
`Get VS Code Executable` in the `VSCode.Helper` library SHALL accept `stable`, `insiders` or a fixed version such as `1.95.0`, and SHALL return the path of the VS Code executable for the current platform. `stable` and `insiders` SHALL resolve to the newest build of that quality, looked up at most once per process. If the update service cannot be reached, they SHALL resolve to the newest cached build of that quality.

#### Scenario: Newest stable build
- **WHEN** `Get VS Code Executable    stable` is called
- **THEN** it returns the executable path of the newest stable VS Code for the current platform

#### Scenario: Fixed version
- **WHEN** `Get VS Code Executable    1.95.0` is called
- **THEN** it returns the executable path of VS Code 1.95.0

#### Scenario: Unknown version
- **WHEN** a version is requested that does not exist
- **THEN** the keyword fails with an error that names the version

#### Scenario: Looked up once
- **WHEN** `stable` is requested several times in one process
- **THEN** the update service is asked once, and every call returns the same executable path

#### Scenario: Update service unreachable
- **WHEN** `stable` is requested, the update service cannot be reached, and a stable build is cached
- **THEN** the keyword returns the executable path of the newest cached stable build

### Requirement: Only complete builds are used
An interrupted, incomplete or corrupted download SHALL never be used. Every download SHALL be verified against the SHA-256 checksum that the update service publishes for the build. A build whose archive contains an entry outside the build folder SHALL never be used. A download SHALL fail with an error instead of waiting forever when the server stops responding. Parallel test processes that request the same uncached build SHALL all get the same executable path.

#### Scenario: Interrupted download
- **WHEN** a download was interrupted in an earlier run
- **THEN** the next call downloads the build again instead of using the partial files

#### Scenario: Checksum mismatch
- **WHEN** the downloaded archive does not match the published checksum
- **THEN** the keyword fails and the cache does not contain that build

#### Scenario: Archive entry outside the build folder
- **WHEN** the archive contains an entry with an absolute path, a path that leaves the build folder, or a link that points outside it
- **THEN** the keyword fails, nothing is written outside the cache, and the cache does not contain that build

#### Scenario: Server stops responding
- **WHEN** the server accepts the connection but stops sending data
- **THEN** the keyword fails with an error after a timeout instead of waiting forever

#### Scenario: Parallel requests
- **WHEN** two test processes request the same uncached build at the same time
- **THEN** both get the same executable path, and the cache holds one complete copy of the build

### Requirement: Supported platforms
Downloads SHALL work on Linux (x64, arm64), Windows (x64) and macOS (x64, arm64). On other operating systems or processor architectures, the keyword SHALL fail with an error that names them, and nothing SHALL be downloaded.

#### Scenario: Linux
- **WHEN** `Get VS Code Executable    stable` runs on Linux x64
- **THEN** the returned path is an executable VS Code binary

#### Scenario: Unsupported architecture
- **WHEN** `Get VS Code Executable` runs on a processor architecture without VS Code builds, such as 32-bit ARM
- **THEN** the keyword fails with an error that names the architecture, and nothing is downloaded
