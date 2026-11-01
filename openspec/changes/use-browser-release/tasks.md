# Tasks

## 1. Browser from PyPI

- [ ] 1.1 In the root `pyproject.toml`, remove the path source of `robotframework-browser` and the clone in `mypy_path`, each with its comment, and add `follow_untyped_imports = true` to the mypy override for `Browser` and `Browser.*`. In `packages/electron/pyproject.toml`, require `robotframework-browser>=21.0.0`. Run `uv lock`; verify with `uv lock --check` and that the diff of `uv.lock` changes only Browser, `grpcio` and `grpcio-tools`.
- [ ] 1.2 Run `uv sync` and `uv run rfbrowser init chromium` in the repository; verify that `uv pip list` shows Browser 21.0.0 without a path, and that `uv run mypy`, `uv run pytest` and `uv run robotcode -r . analyze code` pass.
- [ ] 1.3 Verify the scenarios "Older Browser library in the environment", "Python that is too old" and "VS Code library" of "Supported versions" with `uv pip install --dry-run` of the two packages in throwaway environments in the scratchpad.

## 2. No check for the hook

- [ ] 2.1 Remove the check for a missing hook and its comment at the top of `robotframeworkElectronLaunch` in `packages/electron/src/Electron/electron.js`, and `test_starts_nothing_without_the_hook` and the scenario `no-hook` of the harness in `packages/electron/tests/test_electron_js.py`; verify with `uv run pytest packages/electron/tests/test_electron_js.py`, whose `adopt-fails` test still covers a failed takeover.
- [ ] 2.2 Run the whole acceptance suite on the new environment; verify that `uv run robotcode -r . -p xvfb robot` passes.

## 3. CI

- [ ] 3.1 In the lint job of `.github/workflows/ci.yml`, remove `defaults`, the `path` of the checkout, the checkout and build of Browser, and `setup-node`, and install with `uv sync --locked`; verify with `uvx --from actionlint-py actionlint .github/workflows/ci.yml`, and that the job's two commands pass in a fresh copy of the repository in the scratchpad, without the clone in reach.
- [ ] 3.2 In the test job, make the same removals, keep `setup-node`, replace the build with a step `uv run rfbrowser init --with-deps chromium` after the installation and before the unit tests, install with `uv sync ${{ matrix.sync || '--locked' }}`, add `--upgrade-package robotframework-browser==21.0.0` to the cell with the lowest versions, and drop the prefix of the artifact paths and the comments about the clone; verify with `actionlint`, and that `UV_PYTHON=3.11 uv sync` with the options of that cell selects Python 3.11, Robot Framework 7.1.1 and Browser 21.0.0 in a throwaway copy.

## 4. Installation in the user guide

- [ ] 4.1 Replace the section "Installation" of `docs/src/content/docs/electron/getting-started.md` and of `docs/src/content/docs/vscode/getting-started.md` with the texts in design.md; verify with `npm ci` and `npm run build` in `docs/`, and that the links resolve.
- [ ] 4.2 Replace the section "ffmpeg" of `docs/src/content/docs/electron/videos.mdx` with the text in design.md, and align the sentence on ffmpeg in the documentation of `record_video` in `packages/electron/src/Electron/__init__.py`; verify with `npm run build` in `docs/` and `uv run pytest packages/electron/tests/test_library.py`.
- [ ] 4.3 Add the text in design.md to the section "VS Code and Electron on CI" of `docs/src/content/docs/running/ci-and-display.mdx`; verify with `npm run build` in `docs/`.
- [ ] 4.4 Verify the scenarios of "Guide on installation" and "Guide on ffmpeg" by following the pages in throwaway environments in the scratchpad, with Node.js and with BrowserBatteries: a test of `windows.robot` passes after the installation, `video.robot` fails with the error that the guide names, and passes after the command that the table names.

## 5. Developer documentation

- [ ] 5.1 In `AGENTS.md`, replace the section "Browser Library Dependency" with a short one: Browser comes from PyPI, `packages/electron/pyproject.toml` has the lowest version, `uv.lock` the version for development and CI, `uv run rfbrowser init chromium` completes it, and after an upgrade `uv run rfbrowser clean-node` comes first. Add the command to the entry on `uv sync`; verify by following the entry in a fresh copy in the scratchpad.
- [ ] 5.2 In `CONTRIBUTING.md`, remove step 2 of the development setup, make step 3 the new step 2 with `uv run rfbrowser init chromium` and without the Browser clone, remove the troubleshooting entries on `inv build` and on rebuilding the clone, and let the entry on video or Chromium tests name `uv run rfbrowser init chromium`; verify that the numbered lists are consistent and the setup commands run in that fresh copy.
- [ ] 5.3 In `README.md`, replace the sentence on setting up the Browser clone, add `uv run rfbrowser init chromium` to the commands, and replace the note on the test `Application And Web Browser`, which no longer exists under that name, with one on `browser_beside.robot` and the video tests. In `dev-docs/background.md`, put the lines on the clone into the past tense with the release of Browser 21.0.0 on 2026-11-01, remove the pointer to `AGENTS.md`, and remove the open decision on CI. Remove `../robotframework-browser` from `.claude/settings.json`. Verify with `git grep -n -i -E "browser clone|\.\./robotframework-browser|inv (build|node-build)"`, which may only find the history in `dev-docs/background.md` and archived changes.

## 6. Integration

- [ ] 6.1 Run `uv run pre-commit run --all-files` and `openspec validate use-browser-release --strict`; verify that both pass.

## Workflow follow-up

- The first CI run after the push checks `rfbrowser init --with-deps` and the cell with the lowest versions.
- Archive the change after that run is green.
