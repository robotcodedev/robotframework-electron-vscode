# Spec Delta

## REMOVED Requirements

### Requirement: Provide an Electron binary of a given version
**Reason**: The library no longer downloads Electron. The test environment provides it before the run.
**Migration**: Install the npm package `electron` in the version that the app needs; in Node, `require('electron')` returns the path of its executable. Pass that path to `Start Electron Application`, for example through a `robot.toml` variable.

### Requirement: Cache downloads
**Reason**: Without downloads there is nothing to cache.
**Migration**: The npm package `electron` caches its downloads in the folder that `electron_config_cache` names, by default the user's cache directory.

### Requirement: Only verified, complete downloads are used
**Reason**: Without downloads the library checks no files.
**Migration**: The npm package `electron` checks the checksums of its downloads.

### Requirement: Local executable
**Reason**: Every start takes a local executable, so the special case goes away.
**Migration**: Pass the executable to `Start Electron Application`.

### Requirement: Independent of Browser state
**Reason**: The keyword `Get Electron Executable` goes away with the downloads.
**Migration**: None needed.

### Requirement: Supported platforms
**Reason**: The platform of a download is now the tool's concern.
**Migration**: The npm package `electron` downloads the build for the platform it runs on.
