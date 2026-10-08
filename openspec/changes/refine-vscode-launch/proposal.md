# Proposal

## Why

Using the VSCode library after `add-vscode-launch` showed three gaps:
- Downloading VS Code is a keyword of the `VSCode` library. For Electron, the same job is a separate `Electron.Helper` library. The two packages should work alike.
- Every instance keeps its directory under the output directory, and nothing ever removes them. After a day of test runs, `results/vscode/` held 98 instances and 1.7 GB.
- VS Code forks such as VSCodium start fine with `executable=`, but installing extensions fails, because the command-line script is looked up as `bin/code` while VSCodium calls it `bin/codium`.

## What Changes

- New library `VSCode.Helper` with `Get VS Code Executable    version=stable    executable=${NONE}    cache_dir=${NONE}`, shaped like `Get Electron Executable`. It downloads and caches VS Code as before. A given `executable` is returned unchanged.
- **BREAKING**: `Download VS Code` is removed from the `VSCode` library; use `Get VS Code Executable` from `VSCode.Helper`. `Open VS Code` keeps its `version`, `executable` and `cache_dir` arguments.
- At the start of a run, the library removes the instance directories that earlier runs left in the output directory, the way Browser cleans its own output folders. Instance directories of the current run are kept.
- VS Code forks work with `executable=`: the command-line script for installing extensions is found by the `applicationName` from the build's `product.json` (for example `codium` or `cursor`). The acceptance tests no longer assume the product name "Visual Studio Code", and the README explains what differs for forks.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `vscode-download`: the keyword is `Get VS Code Executable` in the `VSCode.Helper` library. It accepts a local executable, and it works without Browser state.
- `vscode-launch`: `Open VS Code` refers to `Get VS Code Executable`, supports VS Code forks given as executable, and earlier runs' instance directories are removed at the start of a run.

## Impact

- `packages/vscode/`: a new `Helper.py`, changes in `__init__.py` and `download.py`, the acceptance tests and the README.
- No new dependency. Nothing changes in the Electron package or the Browser hook.
