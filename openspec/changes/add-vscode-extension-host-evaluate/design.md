# Design

## Context

The motivation is in proposal.md, and the behaviour is in the specs. These facts from spikes with VS Code 1.141 shape the approach:

- **The extension host is a utility process of the main process**, one per workbench window. Its name, such as `extensionHost-4`, comes from a counter shared by all utility processes. The name does not contain the window id, and the extension host knows neither its window id nor its renderer.
- **Moved editors stay with their window.** An editor moved into its own window (`Move Editor into New Window`) runs in the renderer of its workbench window: `window.opener` is that window, and no extension host is added. `File > New Window` opens a workbench window with its own renderer and its own extension host.
- **A workspace is open in at most one window.** `code --new-window folder-a` in a running instance whose window already shows `folder-a` opens no second window.
- **Several development extensions load side by side.** VS Code accepts several `--extensionDevelopmentPath` arguments and activates all the extensions. [instance.py](../../../packages/vscode/src/VSCode/instance.py) already passes one argument per path.
- **The constructor needs a new signature.** The `VSCode` constructor takes Browser's signature through `functools.update_wrapper`, so `__wrapped__` points to Browser's `__init__`. A new import argument needs its own signature.

## Goals / Non-Goals

**Goals:**
- Use VS Code's public extension API, in every VS Code version and fork that `Open VS Code` starts, without a build step for the helper.
- Need no change to the Browser library.

**Non-Goals:**
- Extension hosts that do not run locally in Node: remote windows (WSL, SSH, containers) and the web worker extension host.
- An argument for a page or an instance. A workspace names a window only within one instance, because two isolated instances can open the same folder. `Switch Electron Application` and `Switch Page` select the instance and the window.
- A keyword that lists the extension hosts. It can follow if tests need it.
- Changes to the example project.

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

### Loaded as a development extension from the package

`Open VS Code` appends the folder of the helper in the installed package as another `--extensionDevelopmentPath`, after the user's paths. Nothing is copied or installed, and prepared extensions directories stay untouched. The helper is plain CommonJS with `"activationEvents": ["*"]`, so that it is ready as early as possible.

Alternatives:
- Installing a `.vsix` with the command-line script into the extensions directory costs a CLI start per instance, and it changes extensions directories that the user prepared.
- Copying the folder into the extensions directory needs an entry in VS Code's `extensions.json`.

**Consequences:**
- Without a development extension of the user's, the window becomes an "Extension Development Host", and its title starts with `[Extension Development Host]`.
- `vscode.extensions.all` lists the helper.
- Both are documented, and `enable_extension_host_evaluation=False` avoids them.

### Import argument with a merged signature

`VSCode.__init__` takes `enable_extension_host_evaluation: bool = True` as a keyword argument and passes the others on to `Electron.__init__`.

Libdoc, Robot Framework's argument conversion and robotlibcore read the signature of `__init__`. So `__init__` gets:
- `__signature__`: Browser's parameters, followed by the new keyword-only parameter;
- `__annotations__`: Browser's annotations, plus `bool` for the new one;
- no `__wrapped__`, because robotlibcore follows it to Browser's signature.

A spike with a subclass showed this on Python 3.10 with Robot Framework 7.1.1, and on Python 3.13 with 7.5:
- Libdoc lists the argument after Browser's;
- `enable_...=True` from Robot data arrives as `bool`, and `timeout=5s` still converts;
- `get_keyword_arguments("__init__")` contains the argument.

Copying Browser's 19 arguments would drift with every Browser release. `Electron` keeps its constructor.

### HTTP on 127.0.0.1 with a token

On activation, the helper:
1. starts an HTTP server on `127.0.0.1` with port 0, so the operating system picks a free port;
2. creates a random token;
3. writes `{port, token, pid, workspace}` into `hosts/<pid>.json` under `context.globalStorageUri`, which is `<user-data>/User/globalStorage/<publisher>.<name>`. It writes a temporary file and renames it, so the file appears complete.

On deactivation it removes the file, but a crashed extension host leaves it behind. The server accepts requests only with the token in a header and answers with status 403 otherwise. The user-data directory belongs to the test run, so the token is as safe as the instance's other data.

The Python side uses `urllib.request`. Its timeout is the library's timeout.

Alternatives:
- A Unix socket or named pipe: `urllib` does not support them, and Windows would need a different path.
- Exchanging files: slow and racy.

### Evaluation in the helper

The helper turns the text into a function with `new Function("return (" + script + ")")()` and calls it with `vscode` and `arg`. It awaits the result and answers:
- `{"result": ...}`, with `null` for `undefined`;
- `{"error": {"message", "stack"}}`, when the function throws or the result cannot be serialised as JSON.

The keyword raises an `AssertionError` with the message. This is the same contract as `Evaluate In Main Process`, with `vscode` in place of `electron`.

An evaluation that outlives the timeout keeps running in the extension host, because JavaScript cannot cancel it. The keyword fails, and the documentation says so.

### Choosing the extension host

The keyword reads the endpoint files of the active instance from the user-data directory that `Open VS Code` recorded. A file counts only while its extension host answers a probe with the token, for example `GET /`. Files whose host refuses the connection or rejects the token are ignored, and the keyword deletes them.

The selection runs in a loop until it finds a host or the library's timeout ends. The loop covers the start of the instance and a reload of the window:

```
workspace given      -> the host whose workspace is that path
exactly one host     -> that host
several hosts        -> workspace of the active page's workbench window
                        -> the host with that workspace
nothing found        -> retry until the timeout, then fail with the
                        workspaces that are open
```

**The workspace of a host:**
- `vscode.workspace.workspaceFile` for a multi-root workspace;
- otherwise the single folder;
- otherwise `null`, for an empty window.

**The workspace of the active page:**
- An expression in the page reads `vscode.context.configuration().workspace` of the workbench window. VS Code's preload script exposes this object. In a window with a moved editor, the expression reads it through `window.opener`.
- The library runs the expression through Browser's `evaluate_javascript` on the active page, so Browser needs no change.

Paths are compared after resolving them, and without regard to case on Windows and macOS. If two hosts have no workspace and the active page's window has none either, the window cannot be determined, and the keyword fails at once.

### Python layout

A module `VSCode/extension_host.py` holds reading the endpoint files, the selection and the request. Unit tests can then use temporary endpoint files and a small `http.server` in a thread, without VS Code. The keyword in `VSCode/__init__.py` connects it with the active instance and the active page.

## Risks / Trade-offs

- [`vscode.context.configuration()` and `window.opener` are VS Code internals] → Only the choice among several windows without `workspace` relies on them. A single window and the `workspace` argument do not. If they change, the keyword fails with a message that `workspace` selects the window.
- [The helper turns every instance without its own development extension into an Extension Development Host] → Documented. `enable_extension_host_evaluation=False` switches the helper off.
- [`await` on a command that opens a quick pick or an input box only settles when the user answers, so the keyword runs into the timeout] → The documentation shows `void vscode.commands.executeCommand(...)` for such commands.
- [Evaluations keep running after a timeout] → Documented. The keyword fails, and the tests should not depend on the evaluation's side effects afterwards.
- [The `"*"` activation event runs the helper in every window] → The helper only starts a server and writes a file, which takes milliseconds.
- [A user's extension may have the same id as the helper] → The helper gets an id with the library's name, which nobody else uses.

## Open Questions

- **Untitled workspaces** (for example from "Duplicate as Workspace in New Window"): `workspaceFile` uses the `untitled:` scheme there. The implementation checks how its path compares with `configPath` of the page. This only affects the choice of such windows through the active page, not the specs.
