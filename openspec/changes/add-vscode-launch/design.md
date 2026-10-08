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
- **Resolution** (checked against the live service on 2026-10-08):
  - `stable` and `insiders` are resolved through `https://update.code.visualstudio.com/api/update/<platform>/<quality>/latest`. Fixed versions go through `https://update.code.visualstudio.com/api/versions/<version>/<platform>/stable`. Both return the download URL, the product version and the SHA-256, so every download is verified. An unknown version gives 404.
  - The quality in the service's URLs is `insider`. The keyword accepts `insiders` and `insider`.
  - Platform names follow `@vscode/test-electron`: `linux-x64`, `linux-arm64`, `win32-x64-archive`, and `darwin-universal` or `darwin-arm64`.
- **Cache:**
  - The cache directory is the `cache_dir` argument, as with `Get Electron Executable`. It defaults to `robotframework-vscode/vscode` in the user's cache directory (`$XDG_CACHE_HOME` or `~/.cache` on Linux, `~/Library/Caches` on macOS, `%LOCALAPPDATA%` on Windows). There is one folder per `<quality>-<product version>-<platform>`.
  - A download is extracted into a temporary folder inside the cache and moved into place with `os.replace`. A folder only exists once it is complete.
  - There is no lock file, the same as in `Electron.Helper`. If parallel processes download the same uncached build, each extracts into its own temporary folder; the first `os.replace` wins, and the others use the folder that is now there. Simple, at the price of a duplicate download on a first parallel run.
- **Executables:** the executable path inside a build follows `@vscode/test-electron` (`code` / `code-insiders` on Linux, `Code.exe` / `Code - Insiders.exe` on Windows, the binary inside the `.app` bundle on macOS). The CLI used to install extensions is `bin/code` (or `bin/code.cmd` on Windows, `Contents/Resources/app/bin/code` on macOS).

Alternative considered: calling `@vscode/test-electron` through npx. It was rejected because users should need nothing from npm.

### Instance directories and launch arguments

- Each `Open VS Code` creates `${OUTPUT DIR}/vscode/<n>/` with `user-data/` and `extensions/`, numbered per run. The directories are not deleted, so the logs stay available.
- Settings are written to `user-data/User/settings.json` before the start. They are the defaults merged with the given settings, which win. The defaults are `workbench.startupEditor: none`, `update.mode: none`, `telemetry.telemetryLevel: off`, `extensions.autoUpdate: false`, `extensions.autoCheckUpdates: false`, `security.workspace.trust.enabled: false`, `editor.accessibilitySupport: off` and `workbench.secondarySideBar.defaultVisibility: hidden`. The last two come from a first run of VS Code 1.141 under Playwright: VS Code detected a screen reader and switched to "Screen Reader Optimized" mode, which changes how the editor behaves, and it opened the Chat view in the secondary side bar.
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

`packages/vscode/atest/fixtures/extension/` is a plain JavaScript extension with no build step (`package.json`, `extension.js`). For this change it contributes one command, `Robot Test: Say Hello`, which shows a notification. `add-vscode-workbench` extends it.

### Tests

- Robot tests live in `packages/vscode/atest/`, and pytest tests in `packages/vscode/tests/`. The download logic is unit-tested with a patched `_open` that serves faked update-service answers, as in `Electron.Helper`.
- Test data follows the Electron tests. A resource holds `${VSCODE_VERSION}` (a fixed version, initially 1.141.0), `${VSCODE_EXECUTABLE}` (`${NONE}`) and `${VSCODE_CACHE}` (the repository's gitignored `.cache/vscode`). `robot.toml` gets a profile `vscode-insiders`. A local VS Code goes into the personal `.robot.toml`.
- `robot.toml` lists both `packages/electron/atest` and `packages/vscode/atest`. Both folders get an `__init__.robot` with `Name    Electron` or `Name    VSCode`, so that the two suites do not both show up as `Atest`.

## Risks / Trade-offs

- [A second start with the same user-data directory is handed over to the running instance] → Every instance gets fresh, numbered directories.
- [VS Code could one day disable the Node inspector that Playwright needs] → Nothing to do now. The CDP fallback remains possible in `Electron`.
- [Executable layout or platform names change, especially on macOS] → Mirror `@vscode/test-electron` and cover them with unit tests.
- [The cache grows with every version] → Document the cache location. No automatic cleanup.
- [Downloads make tests slow and depend on the network] → Use the cache. `Download VS Code` can run in a CI setup step.
