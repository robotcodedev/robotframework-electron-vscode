# Tasks

## 1. Command line

- [ ] 1.1 Move the build selection of `Open VS Code` (`version`, `executable`, `cache_dir`) into a function in `download.py` and use it in `Open VS Code`. Verify with `uv run pytest` and the acceptance tests of `Open VS Code`.
- [ ] 1.2 Add `Run VS Code CLI` to `VSCode.Helper`:
  - required extensions and user-data directories, made absolute;
  - a `ValueError` for `--extensions-dir` or `--user-data-dir` in `args`;
  - the clean environment and the time limit;
  - the output as the return value, and a `RuntimeError` with the script's output on an error.

  Add unit tests with the fake command-line script for the arguments, the environment, both errors and the time limit. Add an acceptance test that installs the test extension's `.vsix` into prepared directories, lists it, and checks that no Node.js process is started.

## 2. Instances

- [ ] 2.1 Add the optional extensions directory to `create_instance_directories` and the argument `extensions_dir` to `Open VS Code`, with documentation that each instance needs its own copy. Add unit tests for the directories. Add an acceptance test that prepares the test extension with `Run VS Code CLI`, copies the directory and opens VS Code with the copy, and that the extension's command works.
- [ ] 2.2 Add `Get VS Code Instance Directories` with documentation. Add an acceptance test for the active instance, for one with `extensions_dir`, for a browser that `Open VS Code` did not start and for a closed instance.
- [ ] 2.3 Remove `Install VS Code Extension`:
  - from the library and its introduction;
  - from the unit tests (`test_library.py`: the added keywords, the tests for unknown and closed instances, the documented exceptions);
  - from `packages/vscode/atest/install_extension.robot`, whose three tests become:
    - "Extension In A Running Instance": the recipe. It gets the directories, installs the test extension's `.vsix` with `Run VS Code CLI`, waits for the shared process log's report and runs the extension's command. Run it five times in a row with `-p xvfb`.
    - "Only The Given Instance Gets The Extension": it opens two instances, installs into the directories of the first by browser id, and checks that the second has no extension.
    - "Closed Instance": moves to the test of `Get VS Code Instance Directories` for a closed instance (task 2.2).

  Verify with `uv run pytest` and `uv run robotcode -r . analyze code`.

## 3. Documentation and example

- [ ] 3.1 Rewrite `docs/src/content/docs/guides/extensions.mdx` with one section per way to get extensions into an instance, as listed in design.md, including the cause of the race and the wait for a running instance. Replace `Install VS Code Extension` in `docs/src/content/docs/getting-started/vscode.md`. Verify the snippets in a scratch suite, and that `npm run build` in `docs/` succeeds with no broken links.
- [ ] 3.2 Update `examples/vscode-extension/tests/python.robot`:
  - add the test "Prepared Before The Start", which prepares `ms-python.python` once into a directory that later runs reuse and opens VS Code with a copy;
  - let "Installed While Running" use `Run VS Code CLI` and the user keyword `Shared Process Log Should Contain` in the example's resources.

  Update the example's README if it describes the tests. Verify with `uv run robotcode -r examples/vscode-extension -p xvfb robot`.

## 4. Verification

- [ ] 4.1 Verify that `uv run pytest`, `uv run pre-commit run --all-files`, all acceptance tests and the example pass locally.
