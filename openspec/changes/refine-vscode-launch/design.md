# Design

## Context

See proposal.md for motivation, and specs/vscode-download/spec.md and specs/vscode-launch/spec.md for the changed requirements. The code comes from `add-vscode-launch`:
- `VSCode/download.py` resolves, downloads and caches builds.
- `VSCode/instance.py` creates the numbered instance directories `<output dir>/vscode/<n>`.
- `VSCode/__init__.py` has the keywords.

`Electron.Helper` is the model for a helper library: a plain Robot Framework class library with `@library`, which holds no Browser state.

A trial run on 2026-10-08 with a portable VSCodium 1.135 (`executable=…/codium`) passed 8 of 12 VSCode acceptance tests:
- Extension installation failed because `cli_path` only knows `bin/code` and `bin/code-insiders`.
- Two tests expected "Visual Studio Code" in the window title.
- VSCodium wrote no `user-data/logs` folder at all.

## Goals / Non-Goals

**Goals:**
- `VSCode.Helper` with the same shape as `Electron.Helper`.
- No unbounded growth of `<output dir>/vscode`.
- Forks work when given as executable, and the test suite can run against one.

**Non-Goals:**
- Downloading forks. `version=` stays limited to Microsoft builds.
- Verifying Cursor in this change; see Open Questions.

## Decisions

### `VSCode.Helper` replaces `Download VS Code`

`VSCode/Helper.py` defines the class `Helper`, decorated with `@library(scope="GLOBAL", version=__version__)`. It has one keyword: `Get VS Code Executable    version=stable    executable=None    cache_dir=None`.
- A given `executable` is returned unchanged.
- Otherwise the keyword calls `download_vscode` and `executable_path`, as `Download VS Code` does today.

`Download VS Code` is removed from `VSCode`, so there is one keyword for one job, as in Electron. `Open VS Code` keeps `version`, `executable` and `cache_dir` and keeps calling the download functions directly.

Alternative considered: keeping `Download VS Code` as an alias. It was rejected because nothing is published yet, and two names for one job would only confuse users.

### Removing earlier instance directories at the first suite start

`VSCode` overrides Browser's listener method `_start_suite`:
- It calls `super()._start_suite(name, attrs)` first.
- On the first call in the process, it removes `<output dir>/vscode`, guarded by a class-level flag. Browser removes its own output folders the same way and at the same moment (`Browser._suite_cleanup_done`).

The actual removal is a function `remove_instance_directories(output_dir)` in `instance.py`, so it can be unit-tested. Only the `vscode` folder is touched.

This is safe because the first suite start in a process comes before any instance of that run. pabot workers have their own output directories. Two independent runs that share one output directory at the same time would clean up each other's folders. That is the same limitation as Browser's cleanup, and the README mentions it.

### Command-line script from `product.json`

`cli_path(executable)` reads `applicationName` from the build's `product.json`. On Linux and Windows that is `resources/app/product.json` next to the executable, on macOS `Contents/Resources/app/product.json`. The script is then `bin/<applicationName>` (`.cmd` on Windows). The existing names `code` and `code-insiders` remain the fallback when `product.json` cannot be read.

Every VS Code build and fork has this field (`code`, `code-insiders`, `codium`, `cursor`), so it works without a list of known forks.

### Acceptance tests that do not assume the product

- The tests check that the workbench is visible (`.monaco-workbench`), not that the title contains "Visual Studio Code".
- The logs test checks a behaviour of VS Code itself, so it gets the tag `vscode-only`.
- A run against a fork uses `-v VSCODE_EXECUTABLE:<fork executable> -e vscode-only`. A test that runs against a fork automatically is not part of this change, because it would need another download of about 100 MB on every new machine.

## Risks / Trade-offs

- [Removing `vscode/` deletes the logs of the previous run] → The current run's logs stay. Anyone who needs older logs uses a separate output directory per run, as with Browser's screenshots and traces.
- [Forks change their layout or CLI] → `applicationName` is the source, with the old names as fallback. A failed lookup ends in an error that names the folder searched.

## Open Questions

- Cursor ships as an AppImage and is untested. If its Electron build has the fuse `EnableNodeCliInspectArguments` switched off, Playwright cannot attach to it. Checking that, by reading the fuse bytes from the binary, can wait until someone needs Cursor. It changes neither this design nor the tasks.
