# Proposal

## Why

`Install VS Code Extension` installs into a running instance with VS Code's command-line script and returns when the script has finished. Whether the running instance notices the new extension is left to VS Code. On CI this fails often: the acceptance test "Extension In A Running Instance" failed in both runs on 2026-10-11 (run 38136863983), with two different causes:

- **Missed install:** VS Code's shared process reads `extensions.json` when it starts and only then begins to watch the file. An extension that the script installs in that window is never reported to the running instance, so its commands never appear. Locally, installs within the first second after the start were always missed, and installs from 1.5 s on were seen. Uninstalling and installing again repairs it.
- **Concurrent write:** the script fails with "Unable to write file '…/extensions/extensions.json' (EntryNotFound (FileSystemError): File to move/copy does not exist)", because the running instance writes `extensions.json` at the same time.

## What Changes

- **Wait until the instance has the extension:** after the script has installed it, `Install VS Code Extension` waits until the instance reports the extension in its shared process log (`Extensions added from another source <id>`).
- **Repair a missed install:** if the report does not come within a short time, the keyword uninstalls the extension and installs it again, once.
- **Retry a concurrent write:** if the script fails because `extensions.json` could not be written, the keyword runs it again, once.
- **Clear failure:** if the instance still does not report the extension, the keyword fails with an error that names the extension and the log file, instead of returning as if it worked.
- **Documentation:** the keyword's documentation says that it returns once the instance has registered the extension.

`Open VS Code` installs its `extensions` before VS Code starts and is not affected.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-launch`: the requirement "Install extensions into a running instance" now requires that the keyword returns once the instance has registered the extension, repairs a missed install, retries a concurrent write of `extensions.json`, and fails clearly if the instance never registers it.

## Impact

- `packages/vscode/src/VSCode/instance.py`: installing into a running instance, with the wait, the repair and the retry.
- `packages/vscode/src/VSCode/__init__.py`: `Install VS Code Extension` uses it, and its documentation.
- `packages/vscode/tests/`: unit tests with a fake command-line script and a fake shared process log.
- `packages/vscode/atest/install_extension.robot`: the existing test "Extension In A Running Instance" is the end-to-end check.
- No change to the Browser library.
