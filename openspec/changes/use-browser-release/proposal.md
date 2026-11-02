# Proposal

## Why

Browser 21.0.0 is released and contains everything the libraries need, so the clone of Browser's `main` in the development setup and in CI has no purpose any more. Nothing but the package metadata says which versions the libraries run on, and its lower bound, `robotframework-browser>=20.6.0`, is wrong, because that release has no `adoptContext` hook.

## What Changes

- **Lowest versions:** the libraries run on Browser 21.0.0, Python 3.11 and Robot Framework 7.1.1 or later.
  - `robotframework-electron` requires `robotframework-browser>=21.0.0`. Robot Framework comes through Browser, and `robotframework-vscode` gets all of it through `robotframework-electron`.
  - The CI cell with the lowest versions tests exactly these three, so it also pins Browser 21.0.0.
- **Installation in the user guide:** `rfbrowser init --skip-browsers` stays the default, because testing an application needs no web browser.
  - The getting-started pages name the lowest versions, show the installation with Node.js and without it, and name the commands for recording videos and for a visible web browser beside an application.
  - The guide on videos says what brings ffmpeg, instead of a Playwright command that cannot be typed as it stands, and names the error without it, which is no longer a timeout.
  - The guide on CI names the system packages, which our own CI installs and the guide does not mention yet.
- **Browser from PyPI:** the workspace takes `robotframework-browser` from PyPI, at the version in `uv.lock`, and `uv run rfbrowser init chromium` completes its installation with what the tests need. The path source and the clone on mypy's path go away, and mypy follows the wheel, which has no `py.typed`.
- **CI:**
  - Checkout and build of Browser go away.
  - The test job runs `rfbrowser init`, and the lint job no longer needs Node.
  - `uv sync --locked` applies everywhere except in the cell with the lowest versions.
  - The repository moves to the root of the workspace of the job, because no clone lies next to it any more.
  - The step that allows the Chromium sandbox on Ubuntu goes away, because Playwright starts Electron without the sandbox on Linux.
- **No check for the hook:** the check for a missing `adoptContext` hook at the start of an application goes away, with its test. The libraries assume a Browser in a suitable version, which the new lower bound ensures.
- **Developer documentation:** `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `dev-docs/background.md` and `.claude/settings.json` no longer describe the clone.

Not part of this change:

- `Record Keyword` and `Record Keywords` on applications; they are tried out separately first.
- The release of the libraries and a publish workflow, which get their own change.
- The upgrade to RobotCode 2.8.0, which belongs to `organize-docs-by-library`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`:
  - New requirements "Supported versions", "Guide on installation", "Guide on ffmpeg" and "Guide on CI runners".
  - In "Failed start", the scenario "Browser cannot take the application over" loses its example of the missing hook.

## Impact

- **Dependencies:** `packages/electron/pyproject.toml`, the root `pyproject.toml` and `uv.lock`. The lock file changes Browser and, because Browser pins it, `grpcio` and `grpcio-tools` from 1.84.0 to 1.85.0.
- **Code:** `packages/electron/src/Electron/electron.js` and `packages/electron/tests/test_electron_js.py`. Keywords do not change.
- **CI:** `.github/workflows/ci.yml`.
- **Documentation:** in `docs/src/content/docs/`, the pages `electron/getting-started.md`, `vscode/getting-started.md`, `electron/videos.mdx` and `running/ci-and-display.mdx`; the documentation of `record_video` in `packages/electron/src/Electron/__init__.py`; and the developer documentation named above.
- **Existing development environments:** they need `uv sync` and `uv run rfbrowser init chromium` once. Without the second command, Browser's error message asks for it.
