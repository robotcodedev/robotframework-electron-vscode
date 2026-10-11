# Tasks

## 1. Electron

- [x] 1.1 Add `color_scheme`, `locale`, `timezone_id` and `bypass_csp` to `New Electron Application`, with documentation, and pass them as `launchOptions` to `electron.js`, which defaults to `colorScheme: null`. Add unit tests in `test_library.py` and `test_electron_js.py`. Verify that `uv run pytest` passes.
- [x] 1.2 Add `--dark`, `--page` and `csp.html` to the fixture app, and the suite `launch_options.robot` with one test per scenario of the `electron-applications` delta. Verify that the Electron acceptance tests pass with `-p xvfb`.
- [x] 1.3 Add the section on launch options to the getting-started page for Electron. Verify that `npm run build` in `docs/` succeeds with no broken links.

## 2. VS Code

- [x] 2.1 Add the four arguments to `Open VS Code`, with documentation that names `--locale` for VS Code's display language, and pass them on. Add the suite `launch_options.robot` with one test per scenario of the `vscode-launch` delta. Verify that `uv run pytest`, the VSCode acceptance tests with `-p xvfb` and `uv run pre-commit run --all-files` pass.
- [x] 2.2 Add `Record Selector` with `bypass_csp` to the Browser features guide. Regenerate the screenshots with `uv run python docs/scripts/update_screenshots.py` and check whether VS Code's look has changed with the new default color scheme. Verify that `npm run build` in `docs/` succeeds.
