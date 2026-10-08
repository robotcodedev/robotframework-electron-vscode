# Proposal

## Why

End-to-end tests of a VS Code extension need a real VS Code: a known version, a clean profile, and the extension under test loaded from source. Today this takes npm tooling such as `@vscode/test-electron` or a hand-written harness. Robot Framework users should get it from one Python library.

## What Changes

- New library `VSCode` (package `robotframework-vscode`), defined as `class VSCode(Electron)`. Importing `VSCode` gives all Browser and Electron keywords plus the VS Code keywords. Like `Electron`, it adds no import arguments.
- VS Code is downloaded and cached in Python, the way `@vscode/test-electron` does it: `stable`, `insiders` or a fixed version, for Linux, Windows and macOS. Users need nothing from npm.
- Keywords open and close an isolated VS Code instance, built on `New Electron Application` and `Close Electron Application`:
  - Each instance gets its own user-data and extensions directories. A second start with the same user-data directory would be handed over to the running instance.
  - `VSCODE_*` variables are removed from the environment.
  - The extension under test is loaded with `--extensionDevelopmentPath`.
  - Optionally, dependency extensions are installed, settings are preset, and a folder or file is opened.
- The instance directories live under the output directory, so VS Code's logs are still there after a failed run.

## Capabilities

### New Capabilities

- `vscode-download`: resolving, downloading and caching VS Code builds per version, quality and platform.
- `vscode-launch`: opening and closing isolated VS Code instances with the extension under test.

### Modified Capabilities

None.

## Impact

- New code in `packages/vscode/`.
- Depends on `add-electron-library`.
- Needs network access to the VS Code update service, and to the Marketplace for dependency extensions, plus a cache directory on disk.
- On Linux without a desktop, VS Code needs a display server such as `xvfb-run -a`. Windows and macOS need nothing extra.
