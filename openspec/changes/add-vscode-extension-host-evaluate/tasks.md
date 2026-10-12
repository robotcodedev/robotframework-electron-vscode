# Tasks

## 1. Helper extension

- [ ] 1.1 Add the helper extension as plain CommonJS in a folder of the `VSCode` package. It needs:
  - a `package.json` with an id that contains the library's name, and `"activationEvents": ["*"]`;
  - an `extension.js` with:
    - an HTTP server on `127.0.0.1` with port 0, and a random token;
    - a probe (`GET`) and an evaluation (`POST`), both rejected with 403 without the token;
    - the endpoint file `hosts/<pid>.json` under `context.globalStorageUri`, holding port, token, pid and workspace, written through a temporary file and a rename;
    - removal of the endpoint file on deactivation.

  Test it in Node with a stub `vscode` module, in the manner of `test_electron_js.py`:
  - a result, `undefined` and a promise;
  - an error message;
  - a result that cannot be serialised;
  - a request without the token;
  - the content of the endpoint file for a folder, a multi-root workspace and an empty window.

  Verify that `uv run pytest` passes.
- [ ] 1.2 Verify that `uv build --package robotframework-vscode` puts the helper's files into the wheel, by listing the wheel's contents.

## 2. Import argument and start

- [ ] 2.1 Give `VSCode.__init__` the keyword argument `enable_extension_host_evaluation: bool = True`:
  - `__signature__` holds Browser's parameters, followed by the new one;
  - `__annotations__` gets the new annotation;
  - `__wrapped__` is not set.

  Describe the argument in the import documentation. Extend the unit test of the import arguments with `timeout=5s` and `enable_extension_host_evaluation=False`. Verify that `uv run pytest` and `uv run mypy` pass.
- [ ] 2.2 Let `Open VS Code` append the helper's folder as the last `--extensionDevelopmentPath` while the argument is `True`, and leave it out with `False`. Add unit tests for both cases that record the start arguments, and verify that `uv run pytest` passes.

## 3. Keyword

- [ ] 3.1 Add `VSCode/extension_host.py`, which:
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
- [ ] 3.2 Add the keyword `Evaluate In Extension Host    function    *lines    arg=None    workspace=None` to `VSCode/__init__.py`:
  - It uses the active instance, with the existing message for applications not started by `Open VS Code`.
  - It fails with a message that names the import argument while the helper is switched off.
  - It reads the active page's workspace through `evaluate_javascript`, with `window.opener` for windows with a moved editor.

  Document every argument, the return value, the exceptions and examples, including `void` for commands that open a quick pick. Update `test_adds_only_its_own_keywords_to_electron`, and add unit tests for the switched-off helper and for a non-VS Code application. Verify that `uv run pytest` passes.
- [ ] 3.3 Add the section "The extension host" to the library introduction. Verify that `uv run robotcode -r . libdoc VSCode <scratch file>` generates the documentation without errors, and that `uv run robotcode -r . analyze code` reports no errors or warnings.

## 4. Acceptance tests

- [ ] 4.1 Add `packages/vscode/atest/extension_host.robot` with a test for each scenario of the `vscode-extension-host` delta, except the switched-off helper. Some scenarios need helpers:
  - **Second windows and moved editors:** open them through the keyword itself, for example with `vscode.openFolder` and `forceNewWindow`, then use `Switch Page    NEW`.
  - **The non-VS Code application:** start VS Code's executable with `New Electron Application`.
  - **The request without the token:** a keyword in `VSCodeFixture.py`.

  Verify that the suite passes with `-p xvfb`.
- [ ] 4.2 Add a suite that imports `VSCode` with `enable_extension_host_evaluation=False` and `timeout=5s`. It covers the scenario "Helper switched off" and the scenario "Browser's import arguments" of the `vscode-launch` delta. Verify that all VSCode acceptance tests pass with `-p xvfb`, and that `analyze code` reports no errors or warnings.

## 5. Guide

- [ ] 5.1 Add the guide "The extension host" to `docs/src/content/docs/guides/` with:
  - when to use the keyword: to prepare and to wait, while checks go through the workbench;
  - a command by its id, and `void` for commands that open something;
  - waiting for diagnostics, and the text of an editor;
  - several windows and `workspace`;
  - switching the helper off and the effects of the helper;
  - the timeout.

  Link the guide from the getting-started page for VS Code and from `packages/vscode/README.md`. Verify:
  - the snippets in a scratch suite against VS Code with `-p xvfb`;
  - that `npm run build` in `docs/` succeeds without broken links.

## 6. Integration

- [ ] 6.1 Verify the whole change:
  - `uv run pre-commit run --all-files`;
  - `uv run pytest`;
  - all acceptance tests with `-p xvfb`;
  - unit tests and VSCode acceptance tests with Python 3.10 and Robot Framework 7.1.1, as in the CI's second cell, in a separate environment through `UV_PROJECT_ENVIRONMENT`.

## Workflow follow-up

- Archive the change after review, and sync the deltas into the main specs.
