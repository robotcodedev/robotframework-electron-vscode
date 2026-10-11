# Design

## Context

`Install VS Code Extension` calls `install_extensions` in `instance.py`. That function runs the instance's command-line script once with `--install-extension`, `--extensions-dir` and `--user-data-dir` and raises `RuntimeError` if the script fails or runs longer than `INSTALL_TIMEOUT`. `Open VS Code` uses the same function before VS Code starts, where no running instance can miss or disturb the install.

The running instance writes its logs to `<user-data>/logs/<session>/`, one session folder per start, named by time, for example `20261011T134207`. When its shared process notices an extension that another process installed, it writes a line like this to `sharedprocess.log` in that folder:

```
2026-10-11 13:41:57.796 [info] Extensions added from another source ms-python.debugpy vscode-userdata:/…/extensions/extensions.json
```

See proposal.md for the two failures.

## Goals / Non-Goals

**Goals:**
- `Install VS Code Extension` returns only when the instance has registered the extension, and repairs the two failures without the test having to do anything.
- The pre-start install of `Open VS Code` stays as it is.

**Non-Goals:**
- Waiting until the extension is activated or its commands are in the palette. That depends on the extension. The keyword's documentation keeps the advice to retry with a freshly opened palette.
- Fixing VS Code's watcher itself.

## Decisions

### The shared process log is the signal

The keyword waits for the line `Extensions added from another source <id>` in `sharedprocess.log`.

- **Why:** it is the running instance's own report that it has taken the extension in. The failure happens exactly when this line is missing.
- **Rejected alternatives:**
  - `extensions.json` and `--list-extensions` describe the disk, which the script has already written, not what the instance knows.
  - Looking for the extension's commands in the workbench would need knowledge about each extension.

**How it is read:**
- The log is the `sharedprocess.log` of the newest session folder under `<user-data>/logs`.
- The keyword remembers the file's size before it runs the script, and reads only what is written after that. A line from an earlier install of the same extension therefore does not count.
- The id is matched without regard to case, followed by a space or the end of the line.

### The extension id

- **Marketplace identifier:** the id is the identifier, without a version suffix (`publisher.name@1.2.3` gives `publisher.name`).
- **`.vsix` file:** the id is `publisher.name` from `extension/package.json` in the archive. The archive is a ZIP file, so the standard library reads it.
- **Unreadable `.vsix`:** if the file has no readable `package.json`, the script reports the error itself. The keyword then fails with the script's message, as it does today.

### Waiting, repair and retry

`install_into_running_instance(cli, extension, directories, env)` in `instance.py` wraps `install_extensions`:

1. Remember the size of the log.
2. Run the script.
   - If it fails and its output mentions `extensions.json`, wait one second and run it once more.
   - Any other failure raises as today.
3. If the script says that the extension is already installed, return. Nothing changed, so the instance will not report anything.
4. Wait for the report, up to `REGISTER_TIMEOUT` (10 s), checking every 0.2 s.
   - Locally, the report came within 0.1 s. The limit leaves room for slow CI runners.
5. **Repair:** if no report came, run the script with `--uninstall-extension <id>` and the same directories, remember the log size again, and install again.
6. Wait once more.
7. If there is still no report, raise `RuntimeError`. The error names the extension and the log file.

**Rejected alternatives:**
- **Always uninstall first:** this would slow every install down, and it does not help with the concurrent write.
- **More than one repair:** once was enough in the local tests. Repeating it would only hide a log format that has changed.
- **Warn and return** instead of failing: a test would then fail later, at a palette command, with a message that does not point to the cause.

## Risks / Trade-offs

- **[A future VS Code changes or drops the log line]** Every install then waits twice, repairs, and fails with an error that names the log. The test run against `vscode-insiders` would show this early. If it happens, the error points to the line that needs adapting.
- **[An installed extension is updated to a newer version]** VS Code may report this differently, for example as removed and added. The wait expects the "added" line for the id, and the newer version should produce it. This is not covered by an acceptance test.
- **[A slow runner needs more than 10 s to report]** The repair runs needlessly and costs some seconds, but the result is still correct.

## Open Questions

- Does VS Code report an update of an already installed extension with the same "added" line? This does not change the approach. If it does not, the wait for updates gets its own handling later.
