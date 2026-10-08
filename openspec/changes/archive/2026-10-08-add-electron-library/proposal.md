# Proposal

## Why

Robot Framework users cannot test Electron applications with the Browser library today. Browser has no Electron support, and the upstream attempt (MarketSquare/robotframework-browser#4695) has stalled. A JavaScript extension also cannot register a context it created itself, so Browser keywords cannot reach the windows of an app that such an extension launched. We want to test arbitrary Electron apps, and the VS Code library builds on this.

## What Changes

- New library `Electron` (package `robotframework-electron`), defined as `class Electron(Browser)`. Projects import `Electron` instead of `Browser` and get every Browser keyword plus the Electron keywords in one library, with one state and one Node process.
- `New Electron Application` starts an Electron app through Playwright's `_electron.launch`, waits for its first window and hands the app's context to Browser, so that `Click`, `Get Text` and the other Browser keywords work on its windows. Each app window is a page in that context.
- `Close Electron Application` closes the app through `Close Browser`. Every way Browser closes things (an explicit close, auto-closing, the end of the run) ends the app, because in Playwright closing an Electron app's context quits the app.
- Browser gets one small, generic hook. It is developed in `../robotframework-browser` on the branch `adopt-context-hook` and proposed upstream. JavaScript extension functions can request `adoptContext`, which registers a context they created in Browser's state. There is no new Browser keyword and no proto change.
- A second, small library `Electron.Helper` provides `Get Electron Executable`. It downloads a given Electron release once, verifies it and caches it, so that projects testing an app from source, and our own tests, get an Electron binary without npm.
- The library adds no import arguments of its own; settings are keyword arguments. Importing it costs no more than importing Browser: it starts no Node process and launches no app.

## Capabilities

### New Capabilities

- `electron-applications`: starting Electron applications, driving their windows with Browser keywords, and closing them again.
- `electron-download`: providing Electron binaries of a given version for the current platform, downloaded and cached.

### Modified Capabilities

None.

## Impact

- New code in `packages/electron/`: the library class, a JavaScript module for the launch, the `Electron.Helper` library, and tests against a small Electron fixture app.
- `Get Electron Executable` needs network access to GitHub releases on first use and a cache directory on disk.
- Depends on the Browser hook. Until it is released, `robotframework-browser` comes from the local clone, so the package cannot be published and CI is deferred.
- Upstream: one small pull request to the Browser library, agreed with the maintainer beforehand.
