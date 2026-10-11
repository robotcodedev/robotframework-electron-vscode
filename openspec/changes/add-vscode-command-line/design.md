# Design

## Context

The building blocks already exist in `packages/vscode/src/VSCode/`:

- **`download.py`** finds and downloads builds (`download_vscode`, `executable_path`, `installed_executable`), and finds the command-line script of an executable, also for forks (`cli_path`).
- **`instance.py`**
  - creates the numbered instance directories (`create_instance_directories` returns root, user-data and extensions);
  - removes the variables that tie a process to a running VS Code (`instance_environment`);
  - builds the launch arguments (`launch_arguments`);
  - runs the script for `extensions` of `Open VS Code` (`install_extensions`, with `INSTALL_TIMEOUT`), which this change removes; the time limit stays as `CLI_TIMEOUT`.
- **`VSCode` library:** `Open VS Code` resolves the build inline from `version`, `executable` and `cache_dir`. The library keeps its instances in a registry by browser id (`_instances()`).
- **`VSCode.Helper`** holds no browser state and offers `Get VS Code Executable`.

See proposal.md for the motivation.

## Goals / Non-Goals

**Goals:**
- One general keyword for VS Code's command line that cannot touch the user's own VS Code by accident.
- Everything else as recipes in the documentation and the example, built from that keyword, `extensions_dir` and Robot Framework's standard libraries.

**Non-Goals:**
- Keywords for single uses, such as preparing, uninstalling or listing extensions. They are recipes.
- Caching extensions inside the library.
- A keyword that waits for a running instance to notice what the script did. The recipe "into a running instance" shows how to wait with Robot Framework's standard libraries.

## Decisions

### `Execute VS Code CLI Command` belongs to `VSCode.Helper`

Preparing extensions happens before any VS Code runs, often in a suite setup. `VSCode.Helper` holds no browser state and already selects builds, so the keyword fits there.

- **Rejected:** putting it in `VSCode`. The keyword needs nothing from the browser state, and the separation between the two libraries would blur.

### Signature and the required directories

`Execute VS Code CLI Command    extensions_dir    user_data_dir    @{args}    version=stable    executable=None    cache_dir=None`

- **Required directories:** both directories are required positional arguments. The keyword passes them as `--extensions-dir=` and `--user-data-dir=`.
  - Relative paths are made absolute against the working directory of the test run, as for `New Electron Application`.
  - If `args` contain `--extensions-dir` or `--user-data-dir` themselves, the keyword fails with a `ValueError`. Two values for the same option would leave it unclear which one the script uses.
- **Selecting the build:** done as in `Open VS Code`. That code moves from `Open VS Code` into a function in `download.py` that both use.
- **Running the script:** without the variables that tie a process to a running VS Code, using `instance_environment(os.environ)`, and with the time limit `CLI_TIMEOUT`, formerly `INSTALL_TIMEOUT` of `install_extensions`.
- **Result:** the keyword returns standard output as text. If the exit code is not 0, it fails with a `RuntimeError` that contains the script's error output, or the standard output if there is none.
- **Rejected:** returning a Process result object, as Robot's Process library does. The output is what tests use, and failing on an error is what `install_extensions` did.

### `Get VS Code Instance Directories` returns a dictionary

The keyword returns `root`, `user_data` and `extensions` as a Robot Framework `DotDict`, so `${dirs.extensions}` and `${dirs}[extensions]` both work. It takes `browser=CURRENT` and finds the instance in the registry, as `Install VS Code Extension` does, with the same error for a browser that `Open VS Code` did not start or that has been closed.

### `extensions_dir` of `Open VS Code`

- **Creating the directories:** `create_instance_directories` gets an optional extensions directory. With it, the instance's root and user-data directory are created as before, and the extensions directory is the given one, made absolute and created if it does not exist.
- **No copy:** the directory is used as it is, without a copy. A running VS Code writes into its extensions directory, so the documentation tells users to give each instance its own copy, for example with `Copy Directory`.
- **Rejected:** copying inside `Open VS Code` (`extensions_from`). That is one more behaviour in the library for something a single standard keyword does.

### `Install VS Code Extension` is removed, and the race is explained in a recipe

The keyword only ran the script with the instance's directories, and it returned before the instance had noticed the extension. On CI this failed in both runs on 2026-10-11:

- **Missed install:** VS Code's shared process reads `extensions.json` when it starts and only then begins to watch it. An install in that window is never reported.
- **Concurrent write:** the script failed because the instance wrote `extensions.json` at the same time.

Instead of fixing the keyword, the recipe "into a running instance" shows the steps:

```robotframework
${dirs} =    Get VS Code Instance Directories
Execute VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --install-extension    ms-python.python
Wait Until Keyword Succeeds    10s    0.2s
...    Shared Process Log Should Contain    ${dirs.user_data}    Extensions added from another source ms-python.python
```

- **`Shared Process Log Should Contain`** is a user keyword in the example's resources. It reads the newest `sharedprocess.log` under `<user-data>/logs`. The newest folder there is not always the right one, because every call of the command-line script adds a log folder of its own, without `sharedprocess.log`.
- **The text explains** why the wait is needed. If the report does not come, the extension should be uninstalled and installed again. If the script fails because `extensions.json` was busy, the call should be repeated.
- **Rejected:** fixing the keyword with a wait, a repair and a retry. The user decided on 2026-10-11 that the libraries offer building blocks and the documentation shows how to combine them. A keyword that is only the script plus a wait does not fit that.

### `extensions` of `Open VS Code` is removed as well

`extensions` was the last place where the library installed extensions itself. On 2026-10-11 the user decided to leave installing to the tests. Then there is one way into an instance before it starts, `Execute VS Code CLI Command` plus `extensions_dir`, which also covers fixed versions, pre-releases and offline runs.

- **The cost:** the common case, one extension at the start, takes two lines instead of one argument.
- **Rejected:** keeping `extensions` as a shortcut. It would be a second way with fewer options, and it would keep a part of the library that installs.

### Recipes

The guide `extensions.mdx` gets one section per way, each with a short snippet:

- from source: `extension_development_path`;
- at the start: prepared with `Execute VS Code CLI Command`, with `id@version` and `--pre-release`, and copied into `extensions_dir`;
- into a running instance: `Execute VS Code CLI Command` and the wait for the instance's report, as shown above;
- prepared once and copied for each test;
- uninstalling and listing with `Execute VS Code CLI Command` and `Get VS Code Instance Directories`;
- disabling extensions with `args`: `--disable-extension`, `--disable-extensions`;
- workspace recommendations read from `.vscode/extensions.json` with Robot's standard libraries;
- profiles, with why they bring little for disposable test instances.

The example project uses the prepared directory and the recipe for a running instance in `python.robot`, so that the snippets of the guide run with the repository's tests.

## Risks / Trade-offs

- **[A prepared directory comes from another VS Code version than the instance]** Extensions can declare an engine version that the instance does not meet. → The recipe prepares with the same `version` variable that opens VS Code.
- **[Instances share one extensions directory]** VS Code writes into it while it runs, and parallel instances can corrupt each other. → The documentation of `extensions_dir` and the recipe say to copy it for each instance.
- **[A script call changes a running instance's extensions]** A running instance may not notice the change. → The recipe "into a running instance" waits for the instance's report and says what to do if it does not come.
- **[Users skip the wait]** Tests that install into a running instance without waiting will be flaky, as ours were. → The guide gives the cause and the wait in the same section as the install.
