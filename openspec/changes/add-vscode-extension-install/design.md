# Design

## Context

See proposal.md for motivation and the spec deltas for the requirements. `Open VS Code` already installs extensions before the start. It calls `install_extension` with the instance's command-line script (`cli_path`, which also finds the scripts of forks), the instance directories and the environment from `instance_environment`, which has no `VSCODE_*` variables. The spike on 2026-10-08 ran the same function against a running VS Code 1.141 instance: the installed extension's command was in the command palette right afterwards, without a reload.

`add-vscode-examples` removed an instance registry from `VSCode` because nothing used it any more. This change adds a record per instance again, for a different purpose.

## Goals / Non-Goals

**Goals:**
- Install a Marketplace extension or a `.vsix` into a running instance with one keyword.
- Exactly the same installation path as `extensions` of `Open VS Code`.

**Non-Goals:**
- Uninstalling or disabling extensions.
- Waiting until the new extension is active. What an extension contributes is workbench content, and tests wait for it with their own keywords, as for every other extension.
- Installing through the Extensions view. That is workbench use and belongs to the user's keywords.

## Decisions

### Keyword

```
Install VS Code Extension    extension    browser=CURRENT
```

- `extension` is a Marketplace identifier or the path of a `.vsix` file, like an entry of `extensions` in `Open VS Code`.
- `browser` is `CURRENT` or a browser id that `Open VS Code` returned. `CURRENT` is resolved with Browser's `Get Browser Ids    ACTIVE`.
- The keyword returns when the command-line script has finished, and fails with the script's error output if it fails, as `Open VS Code` does.

### Record per instance

`Open VS Code` records each instance it starts under its browser id, as an `Instance` with the executable and the instance directories. It records the instance after the workbench is ready, when it returns the ids. `Install VS Code Extension` looks the browser id up there. An unknown id raises an error that names it and says that only instances started by `Open VS Code` are supported.

Records of closed instances stay until the library instance ends. They are small, and an install into a closed instance fails in the command-line script anyway.

### Environment

The keyword builds the environment with `instance_environment(os.environ)` when it is called, as `Open VS Code` does when it starts the instance. The record does not store an environment.

### Tests

- **pytest:**
  - The boundary test from `add-vscode-examples` now expects `Install VS Code Extension` in addition to `Open VS Code` and `Close VS Code`.
  - A unit test checks the error for an unknown browser id. It needs no running instance.
- **Acceptance test:**
  - A helper in `VSCodeFixture.py` packs the test extension into a `.vsix` in the output directory: a zip with `extension.vsixmanifest`, `[Content_Types].xml` and the folder under `extension/`. The spike showed that VS Code's command-line script accepts such a file. It needs no `vsce` and no binary file in the repository.
  - A test opens VS Code without the test extension, installs the packed `.vsix` and runs the extension's command.
  - The same test checks that the extension is not in the user's own extensions, with the existing `List User Extensions`.

## Risks / Trade-offs

- [A future VS Code release no longer picks up extensions installed into a running instance] → The acceptance test runs the command right after the install and would show it. The keyword's documentation then says that a reload is needed, and the profile `vscode-insiders` shows such a change early.
- [Marketplace downloads need network access] → As for `extensions` of `Open VS Code`. The acceptance test uses a packed `.vsix` and needs no network.
