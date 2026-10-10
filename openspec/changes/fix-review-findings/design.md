# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements. Findings of the review on 2026-10-10:
- **Working directory:** Browser's Node process runs in Browser's own folder. `_electron.launch()` without `cwd` gives the application that folder, and Node resolves a relative `executablePath` and `cwd` against it.
- **Leaking process:** `electron.js` closes the application only when `firstWindow()` fails. With a Browser release without the hook, `adoptContext` is the string `RESERVED`, and calling it throws after the launch.
- **`pageId`:** `adoptContext` leaves `pageId` out when the context has no page at that moment, and the library reads it with `adopted["pageId"]`.
- **Extraction:** `extract_zip` joins the entry name to the target folder and creates symlinks as given. Python before 3.12 has no extraction filter for tar archives.
- **Timeouts:** `urlopen` and the VS Code command-line script run without a timeout.
- **VS Code executable:** `Open VS Code` looks for the command-line script and the version next to the executable as given, without following `PATH` or symlinks.
- **Closed instances:** the instance registry keeps the ids of closed instances, so `Install VS Code Extension` installs into a closed instance.
- **Architectures:** both platform functions map every machine that is not arm64 to x64.
- **Duplication:** the Electron download reads the archive into memory to hash it, while the VS Code download streams it, and both have their own `_open` and download steps.

## Goals / Non-Goals

**Goals:**
- Paths that behave as users expect from the test run's point of view.
- No leaking processes, no writes outside the cache, no endless waits.
- One implementation of the download steps.

**Non-Goals:**
- Changes to the Browser library. None of the findings needs one.
- A configurable timeout per keyword. Fixed limits that are generous for the slowest expected case are enough for now.

## Decisions

- **Paths in Python.** `New Electron Application` makes the executable found by `shutil.which` absolute and resolves `cwd` against `os.getcwd()`, defaulting to it. The JavaScript side gets only absolute paths. Arguments in `args` stay as given, because they now resolve against the test run's directory through the application's working directory.
- **Cleanup in `electron.js`.** Everything after the launch runs in a `try` block that closes the application on any error, or kills its process if closing fails. A missing hook is detected before the launch and reported as "The Browser library has no adoptContext hook", so nothing is started at all.
- **Missing `pageId`.** The library reads it with a default of an empty string. Browser indexes later windows anyway, so `Switch Page` finds them.
- **Safe extraction in `Electron.Helper`.** Every entry is checked against the resolved target folder before anything is written. Symlinks are created after all files, and their targets must stay inside the folder, which the macOS application bundles' relative framework links do. Tar archives get the same check on every Python version, in addition to the `tar` filter where it exists.
- **Shared download steps.** `Electron.Helper` provides `open_url` with a timeout of 60 seconds per network operation, a streaming `sha256`, `download` to a file, and the safe extraction. The VS Code download imports them, as it already imports `extract_zip`.
- **Install timeout.** The command-line script gets 10 minutes per call, enough for the Python extension with its dependencies on a slow CI runner. All `extensions` of `Open VS Code` go into one call with several `--install-extension` options.
- **Resolving the VS Code executable.** `Open VS Code` applies `shutil.which` and `Path.resolve()` to a given executable and starts the resolved file. It fails with a `ValueError` if nothing is found, as `New Electron Application` does.
- **The original error.** When the workbench does not become ready, closing the instance runs in its own `try` block. A failure there is logged, and the original error is raised.
- **Closed instances.** `Install VS Code Extension` accepts only ids that Browser still lists, and the registry drops the others whenever it is read.
- **Architectures.** `x86_64` and `amd64` map to x64, `arm64` and `aarch64` to arm64, and every other machine raises a `ValueError` that names it.
- **`stable` and `insiders`.** A module-level dictionary keeps the resolved build per quality and platform for the process. If the update service cannot be reached, the newest cached folder of that quality is used, ordered by version.
- **Test fixtures.** The paths that the fixtures give to `pgrep -f` are escaped with `re.escape`.

## Risks / Trade-offs

- [A slow network can make a download time out after 60 seconds without data] → 60 seconds without any data is long, and the error names the URL.
- [Ten minutes can be too short for very slow runners] → The error names the extension, and the limit is a constant that can be raised.
- [A `stable` run that started before a new release keeps the older build for the rest of the process] → That keeps a run consistent, and the next run picks up the new build.
