# Tasks

## 1. Electron

- [ ] 1.1 Add `bypass_csp` to `New Electron Application` and `electron.js`, with documentation. Add `csp.html` and the `--page` argument to the fixture app. Add acceptance tests for "Script added to a page with a strict policy" and "Policy enforced by default". Verify that `uv run pytest` and the Electron acceptance tests pass.

## 2. VS Code

- [ ] 2.1 Add `bypass_csp` to `Open VS Code` and an acceptance test for "Script added to the workbench". Verify that the VSCode acceptance tests pass and that `analyze code` reports no errors or warnings.

## 3. Documentation

- [ ] 3.1 Add `Record Selector` with `bypass_csp` to the Browser features guide and a sentence to the getting-started page for Electron. Verify that `npm run build` in `docs/` succeeds with no broken links.
