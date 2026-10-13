# Design

## Context

The motivation is in proposal.md, and the behaviour is in the specs. The current state:

- **Downloads in the libraries:**
  - `VSCode/download.py` resolves, downloads, verifies and caches VS Code builds. `Open VS Code` and `Execute VS Code CLI Command` call it through `select_build(version, executable, cache_dir)`.
  - `Electron/Helper.py` does the same for Electron releases.
- **Code that stays:** a few functions of `download.py` work on any installed VS Code, not on downloads:
  - `installed_executable` resolves a command on `PATH` or a symbolic link;
  - `cli_path` finds the command-line script next to an executable, also for forks;
  - `product_version` reads the version for the log.
- **Instance folders:** `instance.py` creates `<output>/vscode/<n>` with a user-data and an extensions directory. A given `extensions_dir` is used in place. `Open VS Code` writes the default settings and the given ones into the user-data directory. The library records each instance with its executable and directories.
- **This repository's tests:**
  - The acceptance tests take `VSCODE_VERSION` and `ELECTRON_VERSION` from their variable resources, and the libraries download those builds into `.cache/`.
  - The profiles `vscode-insiders` and `electron-previous` change the versions.
  - The CI downloads both builds in every run.
- **Tools, from spikes on 2026-10-13:**
  - `@vscode/test-electron` 3.1.0: `downloadAndUnzipVSCode({ version, cachePath })` downloads `stable`, `insiders` or a fixed version, such as `1.141.0`, for Linux, macOS and Windows, also on ARM. It returns the executable's path, on Linux `<cachePath>/vscode-linux-x64-1.141.0/code`. A second call takes the build from the cache without downloading.
  - The npm package `electron` 44.7.0: `require('electron')` in Node returns the executable, `node_modules/electron/dist/electron` on Linux. It downloads the binary only on the first `require`, into the folder named by `electron_config_cache`, by default the user's cache directory. An npm alias, such as `electron-previous` for `npm:electron@42.11.12`, holds a second version next to the first.
- **Order:** this change builds on `add-vscode-extension-host-evaluate`. That change is applied and archived first; this one renames keywords in its capability.

## Goals / Non-Goals

**Goals:**
- The libraries start what the test gives them, and nothing else.
- `Start VS Code` and `Execute VS Code CLI Command` resolve an environment in the same way, so the same arguments mean the same VS Code and the same directories.
- This repository prepares its VS Code and Electron builds before the tests, with ready-made tools, and configures them with `robot.toml` variables and profiles, as users are meant to.

**Non-Goals:**
- A command-line tool of our own that prepares environments. It can follow if the ready-made tools fall short.
- Keeping VS Code from writing to the user's home directory, with VS Code's portable mode. A change of its own follows.
- Copying given directories, or merging settings into them.
- Changes to closing, recording, the extension host or the Electron main process.

## Decisions

### `Start VS Code` and `Start Electron Application`

`Start VS Code    executable    path=None    extension_development_path=None    extensions_dir=None    user_data_dir=None    settings=None    args=None    timeout=60s    ...`
- The executable is the first argument, and it is required: it is the one thing that every start needs. `Start Electron Application` has its executable first as well, as `executable_path` does today. The Electron keyword keeps Playwright's name for the argument.
- `installed_executable` resolves a command on `PATH` and symbolic links, as today.
- The launch, recording and timeout arguments stay as they are.
- The old names get no aliases, because the libraries are in their pilot phase.

**Alternatives:**
- **`executable` as a required named argument:** every call would grow by `executable=`.
- **A default of `code` from `PATH`:** a test would start whichever VS Code the machine happens to have, and the choice that the person running the tests makes would be hidden.

### One rule for the directories

`instance.py` gets one function that `Start VS Code` and `Execute VS Code CLI Command` both use. It creates the next folder `<output>/vscode/<n>`:
- **Given directories** are used in place, as absolute paths. The library writes nothing into them.
- **Directories that are not given** are created fresh in the folder: `user-data` and `extensions`, as today.

The library records the executable and the directories of each instance, as today. `Get VS Code Instance Directories` returns them, given ones included.

### Settings only in the library's own user data

`Start VS Code` writes its default settings and `settings` into a user-data directory that it created, as today. A given user-data directory belongs to the test environment, so:
- the keyword writes no settings into it;
- `settings` together with `user_data_dir` fails before anything starts, with a message that names both arguments.

The quiet-start arguments, such as `--skip-welcome` and `--disable-workspace-trust`, apply in both cases. The keyword's documentation lists the default settings, so that a prepared user-data directory can take them over, for example `editor.accessibilitySupport: off`, without which VS Code detects a screen reader under Playwright.

**Alternatives:**
- **Merging the settings into the given `settings.json`:** this changes a prepared directory with every start.
- **Copying the given directory into the instance's folder:** this is slow for large extensions directories, and it hides which directory a test works on.

### `Execute VS Code CLI Command` in the `VSCode` library

`Execute VS Code CLI Command    *args    executable=None    user_data_dir=None    extensions_dir=None`

The environment arguments are named-only, after the script's arguments. There are two cases:
- **None of the three:** the keyword uses the active instance: its recorded executable, its directories and the environment that the instance got. Without an open instance, it fails with a message that names `executable`.
- **`executable`:** the keyword resolves the directories by the rule above. It is the environment that `Start VS Code` gets with the same arguments. Missing directories are created fresh in a folder of their own, which keeps the script's logs like an instance folder. `user_data_dir` or `extensions_dir` without `executable` fail, so that a call never mixes a given directory with the active instance.

`cli_path` finds the script, `run_cli` runs it, and the keyword still refuses `--extensions-dir` and `--user-data-dir` in `args`. The keyword touches neither Playwright nor Browser's state, so a suite setup can call it before any start.

**Alternatives:**
- **Only the same arguments, without the instance case:** every call on a running VS Code would first read its directories with `Get VS Code Instance Directories`, as today.
- **Only the instance case:** an extensions directory could not be prepared before the start.
- **Given arguments that override the active instance's:** a reader could not tell which environment a call works on.

### No window from the command-line script

VS Code's script runs a command, such as `--install-extension`, and returns. Without a command, it starts VS Code's window instead and returns at once, with success. An empty value makes it ignore an option: in a manual check on 2026-10-13, `--install-extension ""` opened a window on the user's desktop.
- **Arguments:** the keyword fails before it runs the script when it gets no arguments for the script or an empty one.
- **Linux:** the script runs without `DISPLAY` and `WAYLAND_DISPLAY`. A window then cannot start, while the commands need no display. The keyword cannot tell such a call from a command without output, so it returns as usual.
- **macOS and Windows:** only the check of the arguments applies.

**Alternatives:**
- **A list of the commands that the keyword accepts:** it would lag behind VS Code and its forks.
- **Failing on empty output:** `--list-extensions` prints nothing for an empty extensions directory.

### No helper libraries

`VSCode/Helper.py`, `VSCode/download.py` and `Electron/Helper.py` are removed, together with their unit tests. `installed_executable`, `cli_path` and `product_version` move into `instance.py`, with their unit tests. `executable_path`, which knows the layout of the download cache, goes away.

### This repository's VS Code and Electron

**Root `package.json`:**
- It is private, with a lock file, and holds three development dependencies:
  - `@vscode/test-electron` 3.1.0;
  - `electron` 44.7.0;
  - `electron-previous` as `npm:electron@42.11.12`.
- Its script `prepare-tests` runs `scripts/prepare_tests.mjs`, which does three things:
  - downloads VS Code 1.141.0 with `@vscode/test-electron` into `.cache/vscode`, and also Insiders when it is given the argument `insiders`;
  - sets `electron_config_cache` to `.cache/electron` and requires both Electron packages, which downloads their binaries there and not into the user's cache directory;
  - prints the executables' paths.

The packaging of the helper extension keeps its own `packages/vscode/package.json` from `add-vscode-extension-host-evaluate`.

**`robot.toml` variables:**
- `VSCODE_EXECUTABLE` and `ELECTRON_EXECUTABLE` point to the Linux x64 paths of these builds, relative to the repository root.
- The profiles `vscode-insiders` and `electron-previous` point them to the other builds.
- On other platforms, a personal `.robot.toml` sets the paths that the script prints. RobotCode's analysis knows the variables from `robot.toml`.
- `VSCODE_VERSION`, `VSCODE_CACHE`, `ELECTRON_VERSION` and `ELECTRON_CACHE` go away from the variable resources.
- Tests that compare a version, such as `1.141.0` from the main process, read the expected version from a variable that the profiles change together with the executable.

**CI:** the test job runs `npm ci` and `npm run prepare-tests` in the repository before the acceptance tests. It does not cache the builds, like today.

**The example:**
- Its `package.json` gets `@vscode/test-electron` 3.1.0, with a lock file, and a script `download-vscode` that downloads VS Code 1.141.0 into its `.cache/vscode`.
- Its `robot.toml` sets `VSCODE_EXECUTABLE` to that VS Code.
- It refers to nothing outside its folder.
- Its prepared extensions are kept per VS Code version, read with `Execute VS Code CLI Command    --version`.

**Alternatives:**
- **A variable file that the script writes:** platform-independent, but the profiles could no longer simply name an executable.
- **Environment variables from the script:** the CI could set them, but a local run would need them in every shell.
- **One profile per platform:** more configuration for the same paths that a personal `.robot.toml` already overrides.

### Documentation

- **Removed:** the guide "Downloads and cache".
- **The guide on VS Code versions:** a profile per VS Code build sets `VSCODE_EXECUTABLE` and the locators that build needs. It shows how to get builds with `@vscode/test-electron` and the npm package `electron`.
- **The getting-started pages:** they begin with providing VS Code or Electron.
- **The CI guide:** its section "Downloads on CI" becomes a section on preparing the builds in a CI job.
- **The guides on forks, extensions and workbench keywords:** they use the new keywords and variables.
- **Also updated:** the library introductions, the READMEs and `docs/scripts/update_screenshots.py`.

## Risks / Trade-offs

- [The paths in `robot.toml` are those of Linux x64] → The CI and the maintainers run Linux x64. Other platforms set the paths that `prepare-tests` prints in a personal `.robot.toml`.
- [The npm package `electron` downloads into the user's cache directory, unless `electron_config_cache` is set] → `prepare-tests` sets it, and the guide on Electron says so.
- [Insiders needs the network on every call, because `@vscode/test-electron` looks for a newer build] → Only the profile `vscode-insiders` uses it. The fixed version works offline from the cache.
- [Every existing test changes, because of the renamed keywords and the required executable] → The libraries are in their pilot phase. The commits and the changelog name the renames.
- [A given user-data directory gets no default settings] → The keyword's documentation lists them. The quiet-start arguments still apply.
- [Given directories are used in place, so parallel runs on the same directories share them] → Documented. The example copies its prepared extensions for each VS Code, as today.
- [On the active instance, a call without a command may reach the running VS Code through its IPC socket, which then opens a window on its own display] → Task 4.2 checks it. Such a window belongs to the test's VS Code, not to the user's desktop session.
- [`Execute VS Code CLI Command` with `executable` creates a folder for directories that are not given] → It is kept with the script's logs, and the next run removes it, like an instance folder.

## Migration Plan

1. Apply and archive `add-vscode-extension-host-evaluate`.
2. Apply this change. After its archive, edit the purposes of `vscode-examples`, `vscode-command-line` and `vscode-extension-host` in `openspec/specs/`, which still name downloads or the old keywords. A delta cannot change a purpose.
3. A change of its own follows: VS Code's portable mode, so that instances stop writing to the user's home directory.
