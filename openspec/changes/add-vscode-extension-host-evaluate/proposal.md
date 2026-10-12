# Proposal

## Why

End-to-end tests of an extension, such as RobotCode's, often need VS Code's extension API to prepare a test or to wait for a state:
- run a command by its id instead of its title in the command palette;
- wait until a language server has answered, instead of repeating a hover until it shows something;
- read the text of an editor or the diagnostics of a file.

The tests should still check through the workbench; the API serves only to prepare and to wait. The `vscode` API exists only in VS Code's extension host. That is a separate process for each workbench window. `Evaluate In Main Process` does not reach it: in VS Code 1.141, the main process has no services or channels to the extension host.

## What Changes

- **New keyword:** `Evaluate In Extension Host    function    *lines    arg=None    workspace=None` in the `VSCode` library.
  - It runs a JavaScript function in the extension host of the active VS Code instance. The function gets the `vscode` module and `arg`, and the keyword returns its result, as `Evaluate In Main Process` does for the main process.
  - `workspace` selects the window by the folder or the `.code-workspace` file that it has open. Without it, the keyword takes the only running extension host. If several are running, it takes the one of the workbench window that shows the active page; `Switch Page` changes it.
- **Helper extension in the package:** a small extension in plain JavaScript. `Open VS Code` loads it as an additional development extension. When activated, it serves the evaluation on `127.0.0.1` with a random port and token. It writes both into its storage directory in the instance's user data, one file per extension host.
- **New import argument:** `enable_extension_host_evaluation`, default `True`, of the `VSCode` library. With `False`, `Open VS Code` does not load the helper extension, and the keyword fails with a message that names the argument. The import arguments stay Browser's, and this one is added to them.
- **Documentation:**
  - the library introduction and the keyword's documentation;
  - a guide about the extension host;
  - the effects of the helper extension. Without a development extension of its own, the window title starts with `[Extension Development Host]`, and `vscode.extensions.all` lists the helper.

## Capabilities

### New Capabilities

- `vscode-extension-host`: running code in the extension host of a VS Code instance, the helper extension that makes it possible, and the choice of the window.

### Modified Capabilities

- `vscode-launch`:
  - the library gets an import argument of its own;
  - its introduction and import documentation mention the extension host.
- `vscode-examples`: `Evaluate In Extension Host` joins the keywords that the library adds to `Electron`. It is no workbench keyword: it does not drive any part of the workbench.

## Impact

- **Library code:**
  - `packages/vscode/src/VSCode/__init__.py`: the import argument and the keyword;
  - `instance.py`: the launch arguments;
  - a new folder with the helper extension. It is shipped in the wheel like `electron.js` in the `Electron` package.
- **Constructor signature:** the `VSCode` constructor no longer takes its signature from Browser through `__wrapped__`. Instead, `__signature__` and `__annotations__` hold Browser's import arguments followed by the new one. A spike showed that Libdoc, Robot Framework's argument conversion and robotlibcore handle this on Python 3.10 with Robot Framework 7.1.1 and on Python 3.13 with 7.5.
- **Tests:** unit tests of the Python side, and acceptance tests against a real VS Code.
- **`docs/`:** the new guide and the getting-started page for VS Code.
- **Dependencies:** none. The Python side uses `urllib`, and the extension uses only Node's built-in modules.
