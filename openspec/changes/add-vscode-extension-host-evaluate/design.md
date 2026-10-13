# Design

## Context

The motivation is in proposal.md, and the behaviour is in the specs. These facts from spikes with VS Code 1.141 shape the approach:

- **The extension host is a utility process of the main process**, one per workbench window. Its name, such as `extensionHost-4`, comes from a counter shared by all utility processes. The name does not contain the window id, and the extension host knows neither its window id nor its renderer.
- **Moved editors stay with their window.** An editor moved into its own window (`Move Editor into New Window`) runs in the renderer of its workbench window: `window.opener` is that window, and no extension host is added. `File > New Window` opens a workbench window with its own renderer and its own extension host.
- **A workspace is open in at most one window.** `code --new-window folder-a` in a running instance whose window already shows `folder-a` opens no second window.
- **Several development extensions load side by side.** VS Code accepts several `--extensionDevelopmentPath` arguments and activates all the extensions. [instance.py](../../../packages/vscode/src/VSCode/instance.py) already passes one argument per path.
- **A `.vsix` installs with the command-line script, also over itself.** `code --install-extension` puts a `.vsix` of the helper into the given extensions directory. Installing a changed `.vsix` with the same version replaces the installed files, with and without `--force`.

## Goals / Non-Goals

**Goals:**
- Use VS Code's public extension API, in every VS Code version and fork that `Open VS Code` starts. The helper is plain JavaScript; only its `.vsix` is packed.
- Leave the helper to the test environment, like the extensions under test: the library loads nothing by itself.
- Need no change to the Browser library.

**Non-Goals:**
- Extension hosts that do not run locally in Node: remote windows (WSL, SSH, containers) and the web worker extension host.
- An argument for a page or an instance. A workspace names a window only within one instance, because two isolated instances can open the same folder. `Switch Electron Application` and `Switch Page` select the instance and the window.
- A keyword that lists the extension hosts. It can follow if tests need it.
- Loading the helper automatically, a keyword that returns its paths, and publishing it in the Marketplace.

## Decisions

### A helper extension, not the Node inspector of the extension host

```
 Robot test (Python)                       VS Code instance
 +------------------------+   HTTP POST    +---------------------------------+
 | Evaluate In Extension  | -------------> | extension host of a window      |
 | Host                   |  127.0.0.1     |  helper extension               |
 |  - read endpoint files |  token header  |   require('vscode')             |
 |  - choose the host     | <------------- |   run function(vscode, arg)     |
 +------------------------+   JSON result  +---------------------------------+
            ^                                        |
            |   <user-data>/User/globalStorage/      |
            +---- <helper id>/hosts/<pid>.json <-----+  written on activation
```

The alternative was `--inspect-extensions=<port>` with `Runtime.evaluate` over CDP. It needs no extension, but the spike showed three problems:
- **No real access to `vscode`.** `require('vscode')` from the inspector fails in VS Code's module interceptor. With `createRequire` on an existing file, it works through a fallback that logs "Could not identify extension for 'vscode' require call" and returns an API without extension identity. That is an internal path, which can change with any release.
- **The port can be the wrong one.** VS Code silently takes one of the next ten ports when the given one is in use, and reports it only in the renderer's console. With parallel instances, the keyword could reach another instance's extension host.
- **Debug mode has side effects.** It starts the extension host with `--nolazy` and opens a debugger without a token, and it clashes with users who debug their extension with `--inspect-extensions`.

### Loaded by the test, as a folder or a `.vsix`

The package contains the helper as the folder `VSCode/extension` and as the file `VSCode/extension-host.vsix`. The helper is plain CommonJS and activates on `"*"`, see "Activation at the start".

`Open VS Code` adds neither. The helper is part of the test environment, like the extensions under test, and that environment is set before VS Code starts. A test loads the helper in one of two ways:
- **As a development extension:** the folder in `extension_development_path`, after the extensions under test.
  - Nothing is installed, so it works with the fresh directories that each instance gets.
  - The folder belongs to the installed library, so the helper always fits it.
  - The window becomes an "Extension Development Host": its title starts with `[Extension Development Host]`, also without an extension of the test's own, and `vscode.extensions.all` lists the helper.
- **Installed:** the `.vsix` in an extensions directory that the test prepares before the start, with `Execute VS Code CLI Command` or `code --install-extension`, and then given as `extensions_dir`.
  - VS Code runs without development mode.
  - An installed helper outlives an update of the library. The keyword notices that by the helper's version, see "The helper's version". Installing the new `.vsix` replaces the old one.

Installing the `.vsix` into an instance that already runs is not one of the ways. It meets the race described in "Installing into a running VS Code", and waiting for the window to take it in would need the helper itself.

**Finding the files:** the documentation shows how to get the paths from the installed package, without a keyword:
- in Robot Framework data, `${{ pathlib.Path(VSCode.__file__).parent / 'extension' }}`, which also works in a `*** Variables ***` section, because inline Python imports both modules by itself;
- in a shell, `python -c "import pathlib, VSCode; print(pathlib.Path(VSCode.__file__).parent / 'extension-host.vsix')"`.

A spike checked both against the installed workspace.

**Alternatives:**
- **Loading the helper automatically**, with an import argument `enable_extension_host_evaluation` that switches it off. This was implemented first.
  - It made every instance an Extension Development Host.
  - The import argument needed a constructor signature merged from Browser's arguments and its own.
  - It was dropped because the test environment is set before the start, and it is the test's, not the library's.
- **A keyword that returns the paths:** not needed while the documentation shows them.
- **The Marketplace:** the helper runs any code that a test sends, and it belongs to one version of the library. It is not an extension for general use.

### Packing the `.vsix` when the package is built

`@vscode/vsce` packs the `.vsix`, and the package's build runs it. Every `uv build` then yields a wheel whose `.vsix` fits it.

**vsce:**
- `packages/vscode/package.json` is private and pins `@vscode/vsce` 4.0.0 as a development dependency, with a lock file. It lies outside the module folder, so `node_modules` stays out of the wheel and out of the helper's folder.
- Its npm script `package-helper` runs in the helper's folder: `vsce package --no-dependencies --allow-star-activation --skip-license --out ../extension-host.vsix`.
  - `--allow-star-activation` accepts the `"*"` activation event, see "Activation at the start".
  - `--skip-license`: the wheel carries the license file, and the helper's `package.json` names the license.
- The helper's `package.json` gets `license`, `repository` and `"files": ["extension.js"]`. With them, vsce 4.0.0 packed the helper in a spike without a warning or a prompt: four files, 3.3 KB.

**Build backend:** uv_build has no build hooks, and the uv documentation points to other backends for build steps. `robotframework-vscode` therefore builds with hatchling and a custom build hook in `hatch_build.py`, the mechanism that hatchling documents for this. `robotframework-electron` keeps uv_build.

**The hook:**
- **In the source tree,** where `packages/vscode/package.json` exists, it runs `npm ci` and `npm run package-helper` before the sdist or the wheel is built. It always packs anew, so that a changed helper or a new version never ships an old `.vsix`.
- **In an unpacked sdist,** which has no `package.json` for vsce, it takes the `.vsix` from the sdist, and fails if it is missing.
- **In an editable build,** for `uv sync`, it does nothing. A development extension needs only the folder.
- hatchling leaves out files that git ignores, so both targets declare the `.vsix` as an artifact.

**sdist:** `uv build` builds the sdist from the source tree, and then the wheel from the sdist. The sdist contains:
- the module with the `.vsix`;
- `hatch_build.py`;
- the README and the license.

It does not contain the npm files. So neither the wheel nor an installation from the sdist needs Node.

**CI, locally and git:**
- **CI:** the build job sets up Node 24 before `uv build`. The test job runs `uv build --package robotframework-vscode` before the acceptance tests. The build writes the `.vsix` into the source tree, where the acceptance test of the installed helper finds it. It also checks the build in both cells of the matrix.
- **Locally:** `uv build --package robotframework-vscode` or the two npm commands write the `.vsix`. Only the acceptance test of the installed helper needs it. AGENTS.md and CONTRIBUTING.md name the commands and Node 22 or later.
- **Git:** `.gitignore` lists the `.vsix` and `packages/vscode/node_modules/`.

**Alternatives:**
- **A CI step before `uv build`, with uv_build:** the build does not know the step, so a local `uv build` ships a wheel without the `.vsix`, or with an old one.
- **The plugin `hatch-jupyter-builder`,** with which JupyterLab extensions run npm in the Python build: it runs `npm install` instead of `npm ci`, and it runs npm on every editable install too.
- **A PEP 517 backend of our own around uv_build:** more code of our own than a hatchling hook.
- **Committing the `.vsix`:** a binary in git that has to be packed again by hand with every change to the helper.
- **`npx @vscode/vsce@4.0.0` without a lock file:** vsce's own dependencies would float.
- **The development dependency in the helper's own `package.json`:** the usual layout of an extension. But `node_modules` and the lock file would lie in the module folder, and the wheel would need exclusions.

### The helper's version

The helper has the version of `robotframework-vscode`, so that the keyword can tell when an installed helper comes from another version of the library.
- **Writing it:** `scripts/update_versions.py` also writes the version into the helper's `package.json`, as a semantic version: `0.2.0.dev12` becomes `0.2.0-dev.12`, and `0.2.0rc1` becomes `0.2.0-rc.1`. `cz bump` commits the file together with the `pyproject.toml` files, so the committed `package.json` holds the version of the last release, as they do.
- **A spike:** vsce 4.0.0 packed `0.2.0-dev.12` without complaint, and VS Code 1.141 installed it as `robotframework-vscode.extension-host@0.2.0-dev.12`.
- **Reporting it:** the endpoint file holds the version from the helper's `package.json`.
- **Checking it:** once the keyword has chosen a host, it compares that host's version with the version of the installed `robotframework-vscode`, through `packaging.version.Version`.
  - `packaging` reads the semantic form as the same version: `0.2.0-dev.12` equals `0.2.0.dev12`, and the same holds for `a`, `b`, `rc` and their development releases. So the library needs no conversion of its own.
  - `packaging` becomes a dependency of `robotframework-vscode`.
- **Another version:** the keyword fails at once, without retrying. The message names both versions and advises installing the `.vsix` of this version of the library.

**Alternatives:**
- **The version only in the `.vsix`,** with `vsce package <version> --no-update-package-json`: the folder would carry another version than the `.vsix`, and the check would have to treat the two ways differently.
- **No check:** an installed helper of an older version of the library could fail in unclear ways after a change to the protocol between library and helper.

### Activation at the start

The helper activates on `"*"`, so that it is ready as early as possible and independent of other extensions. `onStartupFinished`, which VS Code recommends and vsce does not warn about, fires only after all `"*"` extensions have finished activating.

Measured with VS Code 1.141, from the end of `Open VS Code` until the endpoint file exists:

| | `"*"` | `onStartupFinished` |
|---|---|---|
| no other extension, 6 runs | 0.07 to 0.41 s | 0.28 to 0.51 s |
| next to a `"*"` extension whose activation takes 5 s, 3 runs | 0.34 to 0.38 s | 5.13 to 5.43 s |

With `onStartupFinished`, an extension under test that activates slowly would delay the helper, and one whose activation hangs would block it. The keyword would then report the helper as not loaded, in exactly the test that looks into the hanging activation. The helper's own activation takes milliseconds: it starts a server and writes a file.

### HTTP on 127.0.0.1 with a token

On activation, the helper:
1. starts an HTTP server on `127.0.0.1` with port 0, so the operating system picks a free port;
2. creates a random token;
3. writes `{port, token, pid, version, workspace, workspaceId}` into `hosts/<pid>.json` under `context.globalStorageUri`, which is `<user-data>/User/globalStorage/<publisher>.<name>`. It writes a temporary file and renames it, so the file appears complete.

On deactivation it removes the file, but a crashed extension host leaves it behind. The server accepts requests only with the token in a header and answers with status 403 otherwise. The user-data directory belongs to the test run, so the token is as safe as the instance's other data.

The Python side uses `urllib.request`. Its timeout is the library's timeout.

Alternatives:
- A Unix socket or named pipe: `urllib` does not support them, and Windows would need a different path.
- Exchanging files: slow and racy.

### Evaluation in the helper

The helper turns the text into a function with `new Function("return (" + script + ")")()` and calls it with `vscode` and `arg`. It awaits the result and answers:
- `{"result": ...}`, with `null` for `undefined`, functions and symbols, which have no JSON;
- `{"error": {"message", "stack"}}`, when the function throws or the result cannot be serialised as JSON.

The keyword raises an `AssertionError` with the message. This is the same contract as `Evaluate In Main Process`, with `vscode` in place of `electron`.

An evaluation that outlives the timeout keeps running in the extension host, because JavaScript cannot cancel it. The keyword fails, and the documentation says so.

### Choosing the extension host

The keyword reads the endpoint files of the active instance from the user-data directory that `Open VS Code` recorded.

**Probe:** a file counts only while its extension host answers a probe, `GET /` with the token, with the process id from the file. The keyword ignores and deletes a file when:
- no connection comes about: the connection is refused, or it times out, as a refused connection on Windows does;
- another process on a reused port rejects the token, answers with something that is not JSON, or answers with another process id.

**Retries:** the selection runs in a loop until it finds a host or the library's timeout ends. The loop covers the start of the instance and a reload of the window. Two errors during a reload also lead to another round:
- **No connection comes about for the function's request.** The host has ended since the probe. Because the connection never existed, the function has not run, and the keyword waits for the next host. A busy host, in contrast, accepts the connection and answers late.
- **The active page cannot be read.** It may be navigating, and the keyword reads it again.

The choice in each round:

```
workspace given          -> the host whose workspace is that path
otherwise                -> workspace id of the active page's workbench window
                            -> the host with that workspace id
page tells no workspace  -> the only host; with several, read the page again
                            until the timeout
nothing found            -> retry until the timeout, then fail with the
                            workspaces that are open
no host at all           -> retry until the timeout, then fail with a message
                            that the helper may not be loaded, with both ways
                            to load it
```

The keyword reads the active page even when only one host answers. A window that has just opened shows its page before its extension host answers. In that moment, the only host is the one of another window, and the function would run there unnoticed.

**The workspace of a host:** the endpoint file holds the workspace twice.
- **Its path, for the `workspace` argument:**
  - `vscode.workspace.workspaceFile` for a multi-root workspace saved as a file;
  - otherwise the single folder;
  - otherwise `null`, for an empty window or an untitled workspace.
- **Its id, for the active page:** VS Code's id of the workspace. It is the name of the folder above `context.storageUri`, which is `<user-data>/User/workspaceStorage/<workspace id>/<extension id>`. In an empty window it is `null`, because `storageUri` is `undefined` there.

**The workspace of the active page:**
- An expression in the page reads `workspace.id` from `vscode.context.resolveConfiguration()` of the workbench window. VS Code's preload script exposes this object. In a window with a moved editor, the expression reads it through `window.opener`.
- `resolveConfiguration()` waits for the configuration. A window that has just opened gets it from the main process a moment after Playwright reports its page; until then, `configuration()` returns `undefined`.
- The library runs the expression through Browser's `evaluate_javascript` on the active page, so Browser needs no change.

**Why two values:** a spike with VS Code 1.141 showed that page and host have the same id for a folder, a `.code-workspace` file, an untitled workspace from "Duplicate as Workspace in New Window", and an editor moved into its own window.
- Comparing ids needs no path normalisation.
- It also works for untitled workspaces, whose `workspaceFile` is only `untitled:<number>`.

**Comparing paths:** paths for the `workspace` argument are compared after resolving them, and without regard to case on Windows and macOS.

**Undeterminable window:** if several hosts have no workspace id and the active page's window has none either, the window cannot be determined, and the keyword fails at once.

### Python layout

A module `VSCode/extension_host.py` holds reading the endpoint files, the selection, the comparison of the versions and the request, with `run_in_extension_host` as its entry. Unit tests can then use temporary endpoint files and a small `http.server` in a thread, without VS Code. The keyword in `VSCode/__init__.py` connects it with the active instance and the active page.

### Installing into a running VS Code

**The mechanism:** VS Code's shared process tracks the installed extensions with an extensions watcher (VS Code 1.141, `sharedProcessMain.js`). On start, its `initialize()`:
1. reads `extensions.json` of every profile into a map;
2. registers the listener that later logs "Extensions added from another source";
3. scans the extension folders on disk and marks every folder that is not in the map for removal (`deleteExtensionsNotInProfiles`), which deletes it.

**Why installs fail:** the command-line script extracts into a temporary folder, renames it into the extensions directory, and then writes `extensions.json`. The file watcher reports the change about 75 ms later. `Open VS Code` returns once the workbench shows, and a trace showed the shared process ready only after that, with the watcher still initializing.

**Two failures in that moment:**
- **Missed:** the map already holds the extension when it is read, so no change is reported, and the window never learns of the extension.
- **Deleted:** the folder is on disk at step 3, but not yet in the map. The watcher deletes it, and then still logs "Extensions added from another source" for the change of `extensions.json`.

There is no log line that marks the end of `initialize()`. "Completed initializing default profile extensions" is missing when the command-line script created `extensions.json` first.

**Measurements** with VS Code 1.141, installing a `.vsix`:

| Install | Load | Runs | Missed | Deleted | Marked for removal, still there |
|---|---|---|---|---|---|
| at once after `Open VS Code` | none | 5 | 1 | 0 | 0 |
| 0.3 s to 3 s after `Open VS Code` | none | 8 | 0 | 0 | 0 |
| at once after `Open VS Code` | 10 busy processes on 20 cores | 56 | 3 | 8 | 2 |
| after waiting for the extension host | 10 or 20 busy processes | 45 | 0 | 0 | 0 |

**What the measurements show:**
- **The log lies when the extension is deleted.** In every deleted case the shared process still logged "Extensions added from another source". Once, the line was missing although the extension had arrived.
- **A marked extension is a later failure.** It still works, but it is listed in `.obsolete`, and VS Code deletes it on the next start with this extensions directory.
- **A second install repairs only a missed extension.** It helped in 3 of 3 missed cases, but in only 1 of 4 deleted ones.
  - If the window had received the extension before VS Code deleted its folder, every later update of the extension host failed with ENOENT on that folder (`$deltaExtensions` in `_createExtensionPathIndex`), even after the folder was back.
  - Reloading the window after the second install brought the extension in, in 2 of 2 such cases.

**Decision:** the example's and the acceptance tests' keywords for installing into the running VS Code:
1. wait for the extension host with `Evaluate In Extension Host` before they install. For that, the example's and the acceptance tests' VS Code loads the helper as a development extension;
2. try the install twice, as before, because the running VS Code can write `extensions.json` at the same time;
3. wait up to ten seconds until `vscode.extensions.getExtension(id)` finds the extension in the extension host. That is what the window has taken in;
4. if it does not come, uninstall the extension, ignoring a failure, install it again and reload the window, so that VS Code reads its extensions anew. Then wait once more. The watcher has long finished starting by then.

Waiting for the extension host makes the race unlikely; the check in the extension host and the repair make the keywords correct when it happens anyway. The reload restarts the extensions of the window, so a test that watches its extension react to the new one would notice it. It happens only after a race, which did not occur once the keywords waited for the extension host.

**Alternatives:**
- **The shared process log**, as before: it misses deleted extensions and raises false alarms.
- **A fixed delay:** what is long enough depends on the load of the machine.
- **The log line "Completed initializing default profile extensions":** it is not always written.
- **A library keyword for installing:** rejected on 2026-10-11. The libraries provide building blocks, and the example shows how to combine them.

**Not tested deterministically:** the repair runs only when the race happens. The acceptance tests cover the normal path, and the measurements above cover the race and the repair.

## Risks / Trade-offs

- [`vscode.context.resolveConfiguration()`, `workspace.id` in it and `window.opener` are VS Code internals] → Only the choice without `workspace` relies on them.
  - If the configuration disappears, a single window still works, because the keyword then takes the only host. With several windows it fails after the timeout, with a message that `workspace` selects the window.
  - If only the place of the workspace id changes, the page looks like an empty window, and the keyword fails after the timeout even with one window. `workspace` still works then.
- [Loaded as a development extension, the helper makes the window an Extension Development Host, also without an extension of the test's own] → Documented. Installing the `.vsix` avoids it.
- [A test that does not load the helper waits for the whole timeout before it fails] → The message names both ways to load the helper.
- [An installed helper from an older version of the library] → The keyword compares the versions and says to install the `.vsix` of this version; installing replaces the old one.
- [Building from the source tree needs Node 22 or later and npm] → Building the wheel from the sdist, installing and using the library need no Node. The CI sets up Node where it builds.
- [Two build backends in one workspace] → Only `robotframework-vscode` has a build step. The hook is short, and the build in CI and the list of the wheel's contents check it.
- [`await` on a command that opens a quick pick or an input box only settles when the user answers, so the keyword runs into the timeout] → The documentation shows `void vscode.commands.executeCommand(...)` for such commands.
- [Evaluations keep running after a timeout] → Documented. The keyword fails, and the tests should not depend on the evaluation's side effects afterwards.
- [Windows without a workspace cannot be told apart] → With several of them, the keyword fails. Right after a second one opens, however, only the first one's extension host answers, and the keyword runs the function there. The guide says so; tests that need several windows open folders.
- [The `"*"` activation event runs the helper in every window] → The helper only starts a server and writes a file, which takes milliseconds.
- [A user's extension may have the same id as the helper] → The helper gets an id with the library's name, which nobody else uses.
