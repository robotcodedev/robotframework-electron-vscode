# Tasks

## 1. VSCode.Helper

- [ ] 1.1 Create `packages/vscode/src/VSCode/Helper.py` with the library class `Helper` and `Get VS Code Executable    version=stable    executable=None    cache_dir=None`, and remove `Download VS Code` from `VSCode`. Verify with pytest:
  - a given executable comes back unchanged without network access;
  - libdoc of `VSCode.Helper` lists only `Get VS Code Executable` with its documentation and starts no process;
  - `VSCode` no longer has `Download VS Code`.
- [ ] 1.2 Replace the acceptance test `download.robot` with a `helper.robot` that imports only `VSCode.Helper` and checks that `Get VS Code Executable` returns an existing executable. Verify with `uv run robotcode -r . robot` for that suite.
- [ ] 1.3 Update the keyword docs, the intro of `VSCode` and the README sections on downloads and the cache for `VSCode.Helper`. Verify that libdoc of `VSCode` and `VSCode.Helper` has no unresolved links beyond Browser's baseline.

## 2. Removing earlier instance directories

- [ ] 2.1 Add `remove_instance_directories(output_dir)` to `instance.py` and override `_start_suite` in `VSCode` (call `super()` first, then remove once per process). Verify with pytest that the function removes `<output dir>/vscode` and nothing else.
- [ ] 2.2 Run `uv run robotcode -r . robot` twice. Verify that after the second run `results/vscode/` holds only that run's instances, numbered from 1, and that instances of different suites of one run are all kept.
- [ ] 2.3 Document the cleanup in the README, including the note about runs that share an output directory at the same time. Verify the text against the behaviour from 2.2.

## 3. VS Code forks

- [ ] 3.1 Make `cli_path` read `applicationName` from the build's `product.json`, with `code` and `code-insiders` as fallback. Verify with pytest for the layouts of VS Code, VS Code Insiders, VSCodium (`bin/codium`), Cursor (`bin/cursor`), Windows (`.cmd`) and macOS.
- [ ] 3.2 Make the acceptance tests product-neutral (check `.monaco-workbench` instead of the title) and tag the logs test `vscode-only`. Verify that all acceptance tests pass with VS Code, and that the VSCode suites pass against a portable VSCodium with `-v VSCODE_EXECUTABLE:<codium> -e vscode-only`.
- [ ] 3.3 Add a README section on VS Code forks: `executable=` instead of `version=`, the fork's own extension gallery (for example Open VSX), running the test suite against a fork, and the open point about Cursor. Verify that the described command for VSCodium runs as written.
