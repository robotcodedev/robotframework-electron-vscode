# Spec Delta

## REMOVED Requirements

### Requirement: Select a VS Code build
**Reason**: The library no longer downloads VS Code. The test environment provides it before the run.
**Migration**: Download VS Code with `@vscode/test-electron`, or use an installed or portable VS Code, and pass its executable to `Start VS Code`. A `robot.toml` variable or profile can hold the path.

### Requirement: Cache builds
**Reason**: Without downloads there is nothing to cache.
**Migration**: `@vscode/test-electron` keeps its downloads in its `cachePath`, by default `.vscode-test`.

### Requirement: Only complete builds are used
**Reason**: Without downloads the library checks no builds.
**Migration**: `@vscode/test-electron` extracts a build completely before it returns its path.

### Requirement: Supported platforms
**Reason**: The platform of a download is now the tool's concern.
**Migration**: `@vscode/test-electron` downloads for Linux, macOS and Windows, including ARM. `Start VS Code` starts any VS Code executable on these platforms.

### Requirement: Local executable
**Reason**: Every start now takes a local executable, so the special case goes away.
**Migration**: Pass the executable to `Start VS Code`, or to `Execute VS Code CLI Command` before an instance runs.

### Requirement: Independent of Browser state
**Reason**: The keyword `Get VS Code Executable` goes away with the downloads.
**Migration**: None needed. `Execute VS Code CLI Command` with `executable` still starts no Playwright process.
