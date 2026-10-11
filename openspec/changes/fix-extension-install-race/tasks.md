# Tasks

## 1. Installing into a running instance

- [ ] 1.1 Add the extension id of a Marketplace identifier (without a version suffix) and of a `.vsix` file (`publisher.name` from `extension/package.json`) to `instance.py`. Add unit tests for both forms, for a version suffix and for upper case.
- [ ] 1.2 Add reading the newest session's `sharedprocess.log` from a remembered size on, and waiting for `Extensions added from another source <id>` with `REGISTER_TIMEOUT`. Add unit tests with a fake log: a report after the remembered size counts, an earlier one does not, and a missing log or session folder counts as no report.
- [ ] 1.3 Add `install_into_running_instance`. It retries the script once when its output mentions `extensions.json`, returns when the script reports the extension as already installed, waits for the report, and repairs a missed install once by uninstalling and installing again. If the extension is still not reported, it raises an error that names the extension and the log. Check the script's exact "already installed" message with the cached VS Code. Add unit tests with the fake command-line script and a fake log, one for each path.

## 2. Keyword

- [ ] 2.1 Let `Install VS Code Extension` use `install_into_running_instance`. Update its documentation: it returns once the instance has registered the extension, and the advice about a freshly opened palette stays. Update the `RuntimeError` under *Raises*. Verify with `uv run pytest` and with the acceptance test "Extension In A Running Instance", run five times in a row with `-p xvfb`.

## 3. Verification

- [ ] 3.1 Verify that `uv run pytest`, `uv run pre-commit run --all-files`, all acceptance tests and the example pass locally, and that the CI run after the push is green.
