# Tasks

## 1. VS Code library

- [x] 1.1 Move `installed_executable`, `cli_path` and `product_version`, with the functions they use, from `VSCode/download.py` into `VSCode/instance.py`, together with their unit tests from `test_download.py`. Give `instance.py` the function for the directories, following design.md:
  - given directories are used in place, as absolute paths;
  - the others are created fresh in the next folder `<output>/vscode/<n>`.

  Add unit tests to `test_instance.py` for:
  - both directories given;
  - one given;
  - none given;
  - a relative path;
  - nothing written into given directories.

  Verify that `uv run pytest` passes.
- [x] 1.2 Rename `Open VS Code` to `Start VS Code`, following design.md:
  - the executable is the required first argument;
  - `version` and `cache_dir` go away, and `user_data_dir` is new;
  - default settings and `settings` go only into a user-data directory that the keyword creates;
  - `settings` together with `user_data_dir` fails before anything starts.

  Document every argument, and list the default settings. Add unit tests that record the start arguments for a given user-data directory, and that check that no settings are written into it, and the error for both arguments. Verify that `uv run pytest` and `uv run mypy` pass.
- [x] 1.3 Move `Execute VS Code CLI Command` into the `VSCode` library with the signature from design.md:
  - without `executable`, `user_data_dir` and `extensions_dir`, it runs on the active instance;
  - with `executable`, it runs on the environment that `Start VS Code` would get;
  - directories without `executable`, and a call without an open instance, fail with messages that name `executable`;
  - a call without arguments for the script, or with an empty one, fails before the script runs;
  - on Linux, the script runs without `DISPLAY`, `WAYLAND_DISPLAY` and `XDG_SESSION_TYPE`.

  Document every argument and both cases with examples. Move the unit tests of the command-line script from `test_helper.py` to `test_library.py`, and add tests with a fake script for both cases, the four errors, and the script's environment without the display variables. Verify that `uv run pytest` passes.
- [x] 1.4 Remove `VSCode/Helper.py`, `VSCode/download.py`, `test_download.py` and `test_helper.py`. Rewrite the library introduction:
  - starting VS Code from an executable;
  - given and fresh directories;
  - the command-line script on the instance and before the start;
  - no section on the helper library.

  Verify that:
  - `uv run pytest` and `uv run mypy` pass;
  - `uv run robotcode -r . libdoc VSCode <scratch file>` generates the documentation without errors;
  - `uv run robotcode -r . analyze code` reports no errors in the library.

## 2. Electron library

- [x] 2.1 Rename `New Electron Application` to `Start Electron Application`, in the keyword, its documentation, the library introduction and `Electron/_docs.py`, and in every keyword of `VSCode` that names it. Update the unit tests. Verify that `uv run pytest` and `uv run mypy` pass, and that the generated documentation of both libraries no longer contains `New Electron Application`.
- [x] 2.2 Remove `Electron/Helper.py` and `packages/electron/tests/test_helper.py`, and the helper library from the introduction. Verify that `uv run pytest` passes, and that libdoc generates the documentation of `Electron` without errors.

## 3. This repository's VS Code and Electron

- [x] 3.1 Add the root `package.json` from design.md, with its lock file:
  - development dependencies `@vscode/test-electron` 3.1.0, `electron` 44.7.0 and `electron-previous` as `npm:electron@42.11.12`;
  - the script `prepare-tests` with `scripts/prepare_tests.mjs`;
  - `node_modules/` in `.gitignore`.

  Verify:
  - `npm ci` and `npm run prepare-tests` put VS Code 1.141.0 into `.cache/vscode` and both Electron binaries into `.cache/electron`, and nothing new into `~/.cache/electron`;
  - the printed paths exist, and their `--version` reports 1.141.0, 44.7.0 and 42.11.12;
  - `npm run prepare-tests -- insiders` adds VS Code Insiders.
- [x] 3.2 Set `VSCODE_EXECUTABLE` and `ELECTRON_EXECUTABLE` in `robot.toml`, and let the profiles `vscode-insiders` and `electron-previous` point them to the other builds:
  - `VSCODE_VERSION`, `VSCODE_CACHE`, `ELECTRON_VERSION` and `ELECTRON_CACHE` go away from the variable resources;
  - tests that compare a version take it from a variable that the profiles change together with the executable.

  Verify that `uv run robotcode -r . analyze code` reports no errors or warnings.
- [x] 3.3 Run `npm ci` and `npm run prepare-tests` in the CI's test job before the acceptance tests. Describe both commands, and that they need Node, in AGENTS.md under "Common Commands" and in CONTRIBUTING.md. Verify that `uv run pre-commit run --all-files` passes, and that the commands work as written there.

## 4. Acceptance tests

- [x] 4.1 Change the Electron acceptance tests:
  - `Start Electron Application` with `${ELECTRON_EXECUTABLE}`;
  - `fixture.resource` and `import_arguments.robot` without `Electron.Helper`;
  - remove the tests of `Get Electron Executable`.

  Verify that the Electron acceptance tests pass with `-p xvfb`, and once with `-p xvfb -p electron-previous`.
- [x] 4.2 Change the VSCode acceptance tests:
  - the resource keyword that starts VS Code calls `Start VS Code` with `${VSCODE_EXECUTABLE}`;
  - `helper.robot` goes away. Its tests of the command-line script move to a suite for the requirements on the command-line script, on the instance and with `executable`;
  - add tests for the scenarios "Executable is required", "Settings with a given user-data directory", "Prepared user data" and "Directories of the active instance" with `user_data_dir`;
  - add tests for the scenarios "Empty argument", "No arguments for the script" and "No window on Linux";
  - check whether `Execute VS Code CLI Command    --disable-extensions` on the active instance opens a window in it, and note the result in design.md;
  - `Install Into Running Instance` calls the command-line script on the active instance, without directories.

  Verify that:
  - all VSCode acceptance tests pass with `-p xvfb`, and once with `-p xvfb -p vscode-insiders` after `npm run prepare-tests -- insiders`;
  - `uv run robotcode -r . analyze code` reports no errors or warnings.

## 5. Example

- [x] 5.1 Let the example download its VS Code:
  - its `package.json` gets `@vscode/test-electron` 3.1.0, with a lock file, and the script `download-vscode`;
  - its `.gitignore` gets `node_modules/`;
  - its `robot.toml` sets `VSCODE_EXECUTABLE`;
  - its resources use `Start VS Code`, and `Execute VS Code CLI Command` on the instance and with `executable`;
  - its prepared extensions are kept per VS Code version, read with `--version`.

  Update the example's README and the guides that include the changed files. Verify:
  - the example's tests pass with `-p xvfb`, including the tests tagged `network`;
  - a copy of the example folder in the scratchpad passes after `npm ci` and `npm run download-vscode` there (scenario "Copied example");
  - `uv run pre-commit run --all-files` passes, which includes RobotCode's analysis of the example.
- [x] 5.2 Let `docs/scripts/update_screenshots.py` use the example's VS Code, and fail with a message that names `npm run download-vscode` when it is missing. Run it, and check that the screenshots in `docs/src/assets/screenshots/` show the workbench as before.

## 6. Documentation

- [x] 6.1 Change the documentation site:
  - remove the guide "Downloads and cache", with its entry in the sidebar and every link to it;
  - rewrite the guide on VS Code versions, following design.md;
  - change the getting-started pages, the section "Downloads on CI" of the CI guide, and the guides on forks, extensions and workbench keywords;
  - change the READMEs of both packages.

  Verify:
  - `npm run build` in `docs/` succeeds without broken links;
  - the changed snippets pass in a scratch suite with `-p xvfb`;
  - `grep` finds `Open VS Code`, `New Electron Application`, `Get VS Code Executable`, `Get Electron Executable` and the helper libraries nowhere in `docs/src`, `packages` and `examples`.

## 7. Integration

- [x] 7.1 Verify the whole change:
  - `uv run pre-commit run --all-files`;
  - `uv run pytest`;
  - all acceptance tests with `-p xvfb`;
  - the example's tests with `-p xvfb`, including the tests tagged `network`;
  - unit tests and acceptance tests with Python 3.10 and Robot Framework 7.1.1, as in the CI's second cell, in a separate environment through `UV_PROJECT_ENVIRONMENT`.

## Workflow follow-up

- Archive this change after `add-vscode-extension-host-evaluate`, and sync the deltas into the main specs. The archive retires `vscode-download` and `electron-download`.
- After the archive, edit the purposes of `vscode-launch`, `vscode-examples`, `vscode-command-line` and `vscode-extension-host` in `openspec/specs/`, which still name downloads, explicit directories or the old keywords.
- Plan the change that moves instances into VS Code's portable mode.
