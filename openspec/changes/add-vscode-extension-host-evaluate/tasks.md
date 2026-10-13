# Tasks

## 1. Helper extension

- [x] 1.1 Add the helper extension as plain CommonJS in a folder of the `VSCode` package. It needs:
  - a `package.json` with an id that contains the library's name, and `"activationEvents": ["*"]`;
  - an `extension.js` with:
    - an HTTP server on `127.0.0.1` with port 0, and a random token;
    - a probe (`GET`) and an evaluation (`POST`), both rejected with 403 without the token;
    - the endpoint file `hosts/<pid>.json` under `context.globalStorageUri`, holding port, token, pid, workspace path and workspace id, written through a temporary file and a rename;
    - removal of the endpoint file on deactivation.

  Test it in Node with a stub `vscode` module, in the manner of `test_electron_js.py`:
  - a result, `undefined` and a promise;
  - an error message;
  - a result that cannot be serialised;
  - a request without the token;
  - the content of the endpoint file for a folder, a multi-root workspace, an untitled workspace and an empty window.

  Verify that `uv run pytest` passes.
- [ ] 1.2 Pack the helper as a `.vsix` with vsce, following design.md:
  - `packages/vscode/package.json`, private, with `@vscode/vsce` 4.0.0 as a development dependency, its lock file, and the npm script `package-helper`;
  - `license`, `repository` and `"files": ["extension.js"]` in the helper's `package.json`;
  - `.gitignore` entries for the `.vsix` and `packages/vscode/node_modules/`.

  Verify:
  - `npm ci` and `npm run package-helper` in `packages/vscode` write `src/VSCode/extension-host.vsix` without a warning;
  - the archive lists `extension/package.json` and `extension/extension.js`;
  - `git status` shows neither the `.vsix` nor `node_modules`.
- [ ] 1.3 Build `robotframework-vscode` with hatchling and the build hook `hatch_build.py`, following design.md:
  - in the source tree, the hook runs `npm ci` and `npm run package-helper`;
  - in an unpacked sdist, it takes the `.vsix` from there and fails without it;
  - in an editable build, it does nothing;
  - both targets declare the `.vsix` as an artifact, and the sdist holds only the module, the hook, the README and the license.

  Verify:
  - `uv build --package robotframework-vscode` writes an sdist and a wheel. The wheel contains the helper's folder and the `.vsix`, and the `.vsix` carries the wheel's version. The sdist contains the `.vsix` and `hatch_build.py`, but no npm files and nothing from `node_modules`.
  - Building the wheel from that sdist with `npm` not on `PATH` succeeds, and the wheel contains the `.vsix` (scenario "Wheel from the source distribution").
  - After the `.vsix` is deleted, `uv sync --reinstall-package robotframework-vscode` runs no npm and writes no `.vsix`.
  - `uv run pytest` passes.
- [ ] 1.4 Give the helper the project's version:
  - `scripts/update_versions.py` also writes the version into the helper's `package.json`, as a semantic version;
  - the `pre_bump_hooks` of `cz bump` add the file;
  - the committed `package.json` holds the current version.

  Extend `scripts/tests/test_update_versions.py` with a release, a development release, a release candidate and an alpha release. Verify that `uv run pytest` passes.
- [ ] 1.5 Build the package in the CI:
  - the build job sets up Node 24 before `uv build`;
  - the test job runs `uv build --package robotframework-vscode` before the acceptance tests.

  Describe in AGENTS.md under "Common Commands" and in CONTRIBUTING.md how the `.vsix` is built, and that it needs Node 22 or later. Verify that `uv run pre-commit run --all-files` passes, and that the commands work as written there.

## 2. Start without the helper

- [ ] 2.1 Remove the import argument `enable_extension_host_evaluation` and everything that came with it:
  - `VSCode.__init__` with the merged signature; the constructor takes Browser's signature as on `main`;
  - the text for own import arguments in `Electron/_docs.py`, and the argument's description in the import documentation;
  - the helper's folder among the development extensions of `Open VS Code`, and the sentence about it in the keyword's documentation.

  Restore the unit tests of the import arguments and of the start arguments as on `main`, so that a start without `extension_development_path` passes no `--extensionDevelopmentPath`. Verify that:
  - `uv run pytest` and `uv run mypy` pass;
  - `git diff main -- packages/electron` is empty.

## 3. Keyword

- [x] 3.1 Add `VSCode/extension_host.py`, which:
  - reads the endpoint files of an instance;
  - probes them, and ignores and deletes the stale ones;
  - chooses the host by `workspace`, or the only one, or the one with the workspace of the active page;
  - retries until the timeout, and fails at once when the choice is ambiguous;
  - sends the evaluation with token and timeout, and turns an error answer into an `AssertionError`.

  Add unit tests with temporary endpoint files and an `http.server` in a thread for:
  - a single host;
  - a host chosen by workspace, including path normalisation;
  - several hosts with the active page's workspace;
  - two windows without a workspace;
  - stale files;
  - a file that appears during the wait;
  - the timeout message with the open workspaces;
  - the function's error message.

  Verify that `uv run pytest` passes.
- [x] 3.2 Add the keyword `Evaluate In Extension Host    function    *lines    arg=None    workspace=None` to `VSCode/__init__.py`:
  - It uses the active instance, with the existing message for applications not started by `Open VS Code`.
  - It reads the active page's workspace through `evaluate_javascript`, with `window.opener` for windows with a moved editor.

  Document every argument, the return value, the exceptions and examples, including `void` for commands that open a quick pick. Update `test_adds_only_its_own_keywords_to_electron`, and add a unit test for a non-VS Code application. Verify that `uv run pytest` passes.
- [ ] 3.3 Rewrite the section "The extension host" of the library introduction:
  - the helper's folder and `.vsix` in the package;
  - both ways to load the helper, with the paths as design.md shows them;
  - the effects of the helper as a development extension.

  Verify that:
  - `uv run robotcode -r . libdoc VSCode <scratch file>` generates the documentation without errors;
  - the generated introduction meets the scenario "The extension host" of the `vscode-launch` delta;
  - `uv run robotcode -r . analyze code` reports no errors or warnings.
- [ ] 3.4 Change the keyword's message for when no extension host answers through the helper until the timeout: the helper may not be loaded, and it is loaded with `extension_development_path` and the helper's folder, or by installing the `.vsix`. The keyword's documentation says that the helper must be loaded and links the section from 3.3. Replace the unit tests of the switched-off helper with one for this message, without endpoint files. Verify that `uv run pytest` passes.
- [ ] 3.5 Compare the versions, following design.md:
  - the helper writes the version from its `package.json` into the endpoint file;
  - the keyword compares it with the version of `robotframework-vscode` through `packaging.version.Version`, and `packaging` becomes a dependency of the package;
  - on another version, it fails at once with both versions and the advice to install the `.vsix` of this version.

  Extend the Node test of the endpoint file with the version. Add unit tests for the same version, a development release in its semantic form, another version and a missing version. Verify that `uv run pytest` and `uv run mypy` pass.

## 4. Acceptance tests

- [x] 4.1 Add `packages/vscode/atest/extension_host.robot` with a test for each scenario of the requirements on the evaluation, its failures, a missing instance, waiting and the choice of the window in the `vscode-extension-host` delta. Some scenarios need helpers:
  - **Second windows and moved editors:** open them through the keyword itself, for example with `vscode.openFolder` and `forceNewWindow`, then use `Switch Page    NEW`.
  - **The non-VS Code application:** start VS Code's executable with `New Electron Application`.
  - **The request without the token:** a keyword in `VSCodeFixture.py`.

  Verify that the suite passes with `-p xvfb`.
- [ ] 4.2 Load the helper in the acceptance tests that use it:
  - in `resources/vscode.resource`, a variable with the helper's folder, taken from the installed package as the documentation shows;
  - a keyword there that opens VS Code with the folder as a further development extension;
  - `extension_host.robot` and `install_extension.robot` use the keyword;
  - `instances.robot` expects the title `robot-test` again.

  Verify that these suites pass with `-p xvfb`. This covers the scenario "As a development extension next to the extension under test".
- [ ] 4.3 Replace `extension_host_off.robot` with a suite for the scenarios "Installed from the `.vsix`", "VS Code without the helper" and "Helper of another version" of the `vscode-extension-host` delta.
  - It imports `VSCode` with `timeout=5s`.
  - It installs the `.vsix` from the package into a prepared extensions directory with `Execute VS Code CLI Command`. If the `.vsix` is missing, it fails with a message that names `uv build --package robotframework-vscode`.
  - For another version, it loads a copy of the helper's folder with a changed version in its `package.json` as a development extension.

  Remove the fixture keywords that only the old suite used. Verify that:
  - all VSCode acceptance tests pass with `-p xvfb`;
  - `uv run robotcode -r . analyze code` reports no errors or warnings.

## 5. Guide

- [x] 5.1 Add the guide "The extension host" to `docs/src/content/docs/guides/` with:
  - when to use the keyword: to prepare and to wait, while checks go through the workbench;
  - a command by its id, and `void` for commands that open something;
  - waiting for diagnostics, and the text of an editor;
  - several windows and `workspace`;
  - the helper extension;
  - the timeout.

  Link the guide from the getting-started page for VS Code and from `packages/vscode/README.md`. Verify:
  - the snippets in a scratch suite against VS Code with `-p xvfb`;
  - that `npm run build` in `docs/` succeeds without broken links.
- [ ] 5.2 Replace the guide's section about switching the helper off with one about loading it:
  - as a development extension, next to the test's own extensions in a list;
  - installed from the `.vsix` into an extensions directory prepared before the start, in Robot Framework with `Execute VS Code CLI Command` and in a shell with `code --install-extension`;
  - the paths from the installed package, in Robot Framework data and in a shell;
  - installing the `.vsix` again after an update of the library, which the keyword asks for when the versions differ;
  - that the helper is not in the Marketplace;
  - the effects of each way.

  Verify:
  - the snippets in a scratch suite against VS Code with `-p xvfb`;
  - the shell command against the installed workspace;
  - that `npm run build` in `docs/` succeeds without broken links.

## 6. Installing into a running VS Code

- [x] 6.1 Change `Install Into Running Instance` in `packages/vscode/atest/resources/vscode.resource`, following design.md:
  - wait for the extension host before the install;
  - keep the second try of the install;
  - wait until `vscode.extensions.getExtension(id)` finds the extension, through a check keyword in `Wait Until Keyword Succeeds`;
  - if it does not come: uninstall, ignoring a failure, install again, reload the window and wait once more.

  Remove `Shared Process Log Should Contain` and the unused `browser` argument. Verify that `install_extension.robot` passes three times in a row with `-p xvfb`, and once more with ten busy processes on the machine.
- [x] 6.2 Change `Install Into Running VS Code` in `examples/vscode-extension/tests/resources/extensions.resource` in the same way. It takes the extension's id as an optional second argument for `.vsix` files, and the documentation of the keyword gives the reasons. Verify that the example's test "Installed While Running" passes with `-p xvfb`, and that `uv run pre-commit run --all-files` reports no errors, which includes RobotCode's analysis of the example.
- [x] 6.3 Rewrite the section "Into the running VS Code" of the guide on extensions:
  - why an install right after the start can be missed or deleted, while the shared process log still reports it;
  - waiting for the extension host and checking with `vscode.extensions.getExtension`;
  - the repair with a second install and a reload, and the second try for the busy `extensions.json`.

  Verify that `npm run build` in `docs/` succeeds.
- [ ] 6.4 Let the example load the helper: `Open Example VS Code` in `examples/vscode-extension/tests/resources/vscode.resource` passes the helper's folder from the installed package as a development extension, next to `${EXECDIR}`. Update the guides that include the changed lines of the example. Verify:
  - the example's tests pass with `-p xvfb`, including the tests tagged `network`;
  - `npm run build` in `docs/` succeeds.

## 7. Integration

- [ ] 7.1 Verify the whole change, with the `.vsix` packed:
  - `uv run pre-commit run --all-files`;
  - `uv run pytest`;
  - all acceptance tests with `-p xvfb`;
  - the example's tests with `-p xvfb`, including the tests tagged `network`;
  - unit tests and VSCode acceptance tests with Python 3.10 and Robot Framework 7.1.1, as in the CI's second cell, in a separate environment through `UV_PROJECT_ENVIRONMENT`.

## Workflow follow-up

- After the push, check the CI run: the test job passes with the `.vsix`, and the build job's wheel contains it with the development version that `update_versions.py` wrote.
- Archive the change after review, and sync the deltas into the main specs.
