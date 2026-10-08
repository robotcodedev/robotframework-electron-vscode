# Design

## Context

See proposal.md for motivation, and specs/vscode-download/spec.md and specs/vscode-launch/spec.md for the required behaviour. This change builds on `add-electron-library`: `New Electron Application` and `Close Electron Application` already start and end an app and hand its windows to Browser.

VS Code is an Electron app. Its main executable can be launched by Playwright's `_electron.launch`, and Microsoft's smoke tests do exactly that. `@vscode/test-electron` is the reference for downloading builds and locating executables. VS Code's `test/automation/src/electron.ts` is the reference for launch arguments.

## Goals / Non-Goals

**Goals:**
- Start VS Code from Python with no npm tooling.
- Make every instance reproducible and isolated.

**Non-Goals:**
- Workbench keywords beyond waiting for readiness. They belong to `add-vscode-workbench`.
- Web-based VS Code (vscode.dev, code-server) and remote extension hosts.
- Calling the `vscode` API from tests.

## Decisions

### Library: `class VSCode(Electron)`

The same pattern as `Electron`:
- no own `__init__`,
- an intro made of the own text plus `Electron.__doc__` (which already contains Browser's),
- an own `ROBOT_LIBRARY_VERSION`,
- keywords as `@keyword` methods.

The keywords are `Download VS Code`, `Open VS Code` and `Close VS Code`.

### Download with the standard library only

`VSCode/download.py` uses `urllib`, `tarfile`, `zipfile` and `hashlib`, so it adds no dependency.
- **Resolution:**
  - `stable` and `insiders` are resolved through `https://update.code.visualstudio.com/api/update/<platform>/<quality>/latest`, which gives the URL, the product version and the SHA-256.
  - Fixed versions are downloaded from `https://update.code.visualstudio.com/<version>/<platform>/stable`.
  - Platform names follow `@vscode/test-electron`: `linux-x64`, `linux-arm64`, `win32-x64-archive`, and `darwin-universal` or `darwin-arm64`.
- **Cache:**
  - The cache lives in `ROBOTFRAMEWORK_VSCODE_CACHE`, or else `~/.cache/robotframework-vscode` (`%LOCALAPPDATA%\robotframework-vscode` on Windows), with one folder per `<quality>-<version>-<platform>`.
  - A download is extracted into a temporary folder inside the cache and moved into place with `os.replace`. A folder only exists once it is complete.
  - A lock file, created with `O_CREAT | O_EXCL` and polled, serialises parallel processes that want the same build.
- **Executables:** the executable path inside a build follows `@vscode/test-electron` (`code` / `code-insiders` on Linux, `Code.exe` / `Code - Insiders.exe` on Windows, the binary inside the `.app` bundle on macOS). The CLI used to install extensions is `bin/code` (or `bin/code.cmd` on Windows, `Contents/Resources/app/bin/code` on macOS).

Alternative considered: calling `@vscode/test-electron` through npx. It was rejected because users should need nothing from npm.

### Instance directories and launch arguments

- Each `Open VS Code` creates `${OUTPUT DIR}/vscode/<n>/` with `user-data/` and `extensions/`, numbered per run. The directories are not deleted, so the logs stay available.
- Settings are written to `user-data/User/settings.json` before the start. They are the defaults merged with the given settings, which win. The defaults are `workbench.startupEditor: none`, `update.mode: none`, `telemetry.telemetryLevel: off`, `extensions.autoUpdate: false`, `extensions.autoCheckUpdates: false` and `security.workspace.trust.enabled: false`.
- Dependency extensions are installed with the CLI (`--install-extension <id|vsix> --extensions-dir … --user-data-dir …`) before the start.
- Launch arguments:
  - `--user-data-dir`, `--extensions-dir`, and one `--extensionDevelopmentPath` per extension folder,
  - `--skip-welcome`, `--skip-release-notes`, `--disable-telemetry`, `--disable-updates`, `--disable-workspace-trust`,
  - `--disable-dev-shm-usage` on Linux,
  - then the caller's extra `args`, then the folder or file to open.
- The environment is a copy of `os.environ` without `VSCODE_*` and `ELECTRON_RUN_AS_NODE`, passed as `env` to `New Electron Application`.
- After the first window opens, `Open VS Code` waits until `.monaco-workbench` is visible. Its timeout defaults to 60 seconds, because a first start on CI is slow.
- The resolved product version is stored per browser id, so that `add-vscode-workbench` can choose version-specific selectors.

### Test extension

`packages/vscode/atest/fixtures/extension/` is a plain JavaScript extension with no build step (`package.json`, `extension.js`). For this change it contributes one command, `Robot Test: Say Hello`, which shows a notification. `add-vscode-workbench` extends it. Robot tests live in `packages/vscode/atest/`. Download logic gets pytest unit tests with a local fake update server.

## Risks / Trade-offs

- [A second start with the same user-data directory is handed over to the running instance] → Every instance gets fresh, numbered directories.
- [The Chromium sandbox fails on some Linux systems (for example Ubuntu 24.04's AppArmor rules)] → Users can pass `--no-sandbox` through `args`. Decide on a default when CI is set up.
- [VS Code could one day disable the Node inspector that Playwright needs] → Nothing to do now. The CDP fallback remains possible in `Electron`.
- [Executable layout or platform names change, especially on macOS] → Mirror `@vscode/test-electron` and cover them with unit tests.
- [The cache grows with every version] → Document the cache location. No automatic cleanup.
- [Downloads make tests slow and depend on the network] → Use the cache. `Download VS Code` can run in a CI setup step.
