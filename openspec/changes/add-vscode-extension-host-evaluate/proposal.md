# Proposal

## Why

End-to-end tests of an extension, such as RobotCode's, often need VS Code's extension API to prepare a test or to wait for a state:
- run a command by its id instead of its title in the command palette;
- wait until a language server has answered, instead of repeating a hover until it shows something;
- read the text of an editor or the diagnostics of a file.

The tests should still check through the workbench; the API serves only to prepare and to wait. The `vscode` API exists only in VS Code's extension host. That is a separate process for each workbench window. `Evaluate In Main Process` does not reach it: in VS Code 1.141, the main process has no services or channels to the extension host.

Installing an extension into a running VS Code needs exactly such a wait, and the wait that the example and the acceptance tests use today is unreliable.
- They wait until VS Code's shared process logs "Extensions added from another source".
- But the workbench shows before the shared process has finished starting. An extension installed in that moment is missed, or deleted again while the log still reports it.
- Under CPU load, 4 of 12 installs right after `Open VS Code` ended with the extension deleted and the line in the log.
- The extension host knows reliably whether the window has taken an extension in.

## What Changes

- **New keyword:** `Evaluate In Extension Host    function    *lines    arg=None    workspace=None` in the `VSCode` library.
  - It runs a JavaScript function in the extension host of the active VS Code instance. The function gets the `vscode` module and `arg`, and the keyword returns its result, as `Evaluate In Main Process` does for the main process.
  - `workspace` selects the window by the folder or the `.code-workspace` file that it has open. Without it, the keyword takes the extension host of the workbench window that shows the active page; `Switch Page` changes it.
- **Helper extension in the package:** a small extension in plain JavaScript. When activated, it serves the evaluation on `127.0.0.1` with a random port and token. It writes both into its storage directory in the instance's user data, one file per extension host.
  - The `VSCode` package contains it twice: as a folder and as a `.vsix` file, which `@vscode/vsce` packs when the package is built.
  - It has the version of `robotframework-vscode`. The keyword compares the versions and fails at once with both of them when an installed helper comes from another version of the library.
  - The library does not load it. Like the extensions under test, it is part of the test environment, which is set before VS Code starts: a test passes the folder as `extension_development_path`, or installs the `.vsix` into an extensions directory that it prepares.
  - It is not published in the Marketplace.
  - Without the helper, the keyword fails after the timeout with a message that says how to load it.
- **Installing into a running VS Code:** the example's `Install Into Running VS Code` and the acceptance tests' `Install Into Running Instance` change in three ways:
  - they wait for the extension host before they install;
  - they check with `vscode.extensions.getExtension` instead of the shared process log whether the window has taken the extension in;
  - if it has not, they install it again.

  The guide on extensions explains why. The example loads the helper as a development extension next to the extension under test.
- **Documentation:**
  - the library introduction and the keyword's documentation;
  - a guide about the extension host;
  - where the installed package keeps the helper's folder and `.vsix`, and how to load each;
  - the effects of the helper as a development extension: the window title starts with `[Extension Development Host]`, also without an extension of the test's own, and `vscode.extensions.all` lists the helper.

## Capabilities

### New Capabilities

- `vscode-extension-host`: running code in the extension host of a VS Code instance, the helper extension that makes it possible and how a test loads it, and the choice of the window.

### Modified Capabilities

- `vscode-launch`: the library introduction gets a section about the extension host.
- `vscode-examples`:
  - `Evaluate In Extension Host` joins the keywords that the library adds to `Electron`. It is no workbench keyword: it does not drive any part of the workbench.
  - The example loads the helper extension and installs into a running VS Code with the extension host instead of the shared process log.

## Impact

- **Library code:**
  - `packages/vscode/src/VSCode/__init__.py`: the keyword and its section in the introduction;
  - `packages/vscode/src/VSCode/extension_host.py`: choosing the extension host and sending it the function;
  - a new folder with the helper extension, shipped in the wheel like `electron.js` in the `Electron` package, and the `.vsix` next to it.
- **Build:**
  - `packages/vscode/package.json` pins `@vscode/vsce` and has an npm script that packs the `.vsix`;
  - `robotframework-vscode` builds with hatchling instead of uv_build, and a build hook packs the `.vsix` during `uv build`. The sdist carries it, so the wheel built from the sdist needs no Node;
  - `scripts/update_versions.py` writes the version into the helper's `package.json` too, and `cz bump` commits it;
  - the CI's build job sets up Node, and its test job builds the package before the acceptance tests;
  - the `.vsix` is a build artifact and is not committed.
- **Tests:** unit tests of the Python side, and acceptance tests against a real VS Code with the helper loaded either way.
- **Installing into a running VS Code:**
  - `examples/vscode-extension/tests/resources/extensions.resource`;
  - `packages/vscode/atest/resources/vscode.resource`;
  - the guide on extensions.
- **`docs/`:** the new guide and the getting-started page for VS Code.
- **Contributing:** AGENTS.md and CONTRIBUTING.md name the commands that pack the `.vsix`.
- **Dependencies:**
  - At run time, `packaging` for comparing the versions. The Python side uses `urllib` for the requests, and the extension uses only Node's built-in modules.
  - Building the package from the source tree needs hatchling, `@vscode/vsce` and Node 22 or later. Building the wheel from the sdist, installing it and using the library need no Node.
