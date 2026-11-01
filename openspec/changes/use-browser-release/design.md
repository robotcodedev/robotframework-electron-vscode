# Design

## Context

The workspace takes Browser from a clone of its `main` next to the repository, through a path source. Developers and CI build that clone by hand. See proposal.md for why this ends.

Measured on 2026-11-01 with the Browser 21.0.0 wheel from PyPI and the code of the libraries unchanged:

| Setup | Result |
|---|---|
| Python 3.13, `rfbrowser init chromium` | 232 unit tests, 195/195 acceptance tests |
| Python 3.11, Robot Framework 7.1.1, `rfbrowser init chromium` | 232 unit tests, 195/195 acceptance tests |
| `rfbrowser init chromium-headless-shell` | 195/195 acceptance tests; 278 MB instead of 681 MB |
| `rfbrowser init --skip-browsers` | `video.robot` 1/3, the others fail at once with `Video recording has not been started` |
| `rfbrowser init --skip-browsers` plus ffmpeg alone | 194/195 acceptance tests; `Web Page Beside An Application` needs a browser |
| BrowserBatteries, no `rfbrowser init` | `windows.robot` 42/42, `video.robot` 1/3 |
| BrowserBatteries, `rfbrowser install --only-shell chromium` | `video.robot` and `browser_beside.robot` 4/4 |
| BrowserBatteries, `rfbrowser install chromium` | `browser_beside.robot` passes |
| Copy of the repository without clone and without `rfbrowser init`, with the `pyproject.toml` of this change | `uv lock` changes only Browser, `grpcio` and `grpcio-tools`; `uv sync --locked` and `pre-commit run --all-files` pass |

## Goals / Non-Goals

**Goals:**

- Developers, CI and users run the same Browser wheel.
- The lowest versions that the libraries promise are the ones that CI tests.

**Non-Goals:**

- Testing BrowserBatteries in CI, or wheels of our own libraries in a clean environment. The second belongs to the release change.
- A way to test against an unreleased Browser. If it is needed again, a temporary path source does it.
- An `rfbrowser` command that installs ffmpeg alone. That would be an addition to Browser.

## Decisions

### A lower bound for Browser, and no upper bound

`robotframework-electron` requires `robotframework-browser>=21.0.0`.

An upper bound such as `<22` would hold users back at every new Browser major until a release of our libraries, and nothing suggests yet that a major breaks the hook. If one does, users see a failed start, and a release with a bound fixes that.

### Development installs what the tests need

`uv sync` installs the wheel, and `uv run rfbrowser init chromium` completes it, because `browser_beside.robot` opens Chromium and the video tests need Playwright's ffmpeg. Both land inside `.venv`, not in `~/.cache` (measured). The size does not matter for the repository's own tests, so there is no reason to narrow this to the headless shell, which would be enough today.

The alternative, BrowserBatteries for development, needs no `rfbrowser init`, but Chromium and ffmpeg would still have to come from somewhere. Node is needed anyway, for the builds of the tests, the helper extension and the documentation site.

### What the user guide tells people

`rfbrowser init --skip-browsers` stays the default: testing an application needs no web browser, and the first test works without one. Everything else is one command of Browser's own tools.

Playwright's ffmpeg is a static build from Playwright's CDN, in a folder next to the browsers, and Playwright looks for it only there. A system ffmpeg is ignored (measured on a machine that has one), so `apt install ffmpeg` does not help, and the revision in the folder name changes with Playwright. Any browser that Browser installs brings ffmpeg along, and the headless shell is the smallest one.

The alternatives for recording videos:

- **A Python one-liner:** `python -c "from Browser import Browser; Browser().execute_npx_playwright('install', 'ffmpeg')"` installs ffmpeg alone, 5 MB instead of 278 MB, with Node.js and without it (measured). The method is not documented by Browser, so the guide does not rely on it.
- **`npx playwright install ffmpeg`:** this is what the guide hints at today. It has to run in Browser's folder inside the environment, whose path contains the Python version.

The text for the section "Installation" of `electron/getting-started.md`:

````md
`robotframework-electron` needs Python 3.11 or later. It brings the Browser library,
21.0.0 or later, and with it Robot Framework, 7.1.1 or later.

With Node.js, `rfbrowser init` completes the installation of the Browser library:

```sh
pip install robotframework-electron
rfbrowser init --skip-browsers
```

Without Node.js, Browser's BrowserBatteries take its place:

```sh
pip install robotframework-electron "robotframework-browser[bb]"
```

An application brings its own Electron, so this is all that testing an application needs.
Two things need more:

| For | With Node.js | Without Node.js |
|---|---|---|
| [Recording videos](../videos/#ffmpeg) | `rfbrowser init chromium-headless-shell` | `rfbrowser install --only-shell chromium` |
| A visible web browser beside an application | `rfbrowser init chromium` | `rfbrowser install chromium` |
````

`vscode/getting-started.md` gets the same text with `robotframework-vscode`, which also brings `robotframework-electron`. There, VS Code brings its own Electron, testing an extension is what needs no more, and the link goes to `../../electron/videos/#ffmpeg`.

The text for the section "ffmpeg" of `electron/videos.mdx`:

```md
Playwright needs its own ffmpeg to record. It comes with any browser that Browser installs,
but not with `--skip-browsers`. The smallest browser is the headless shell, see
[Installation](../getting-started/#installation). Without ffmpeg, `Start Electron Application`
fails with `Video recording has not been started`.
```

The text for the section "VS Code and Electron on CI" of `running/ci-and-display.mdx`:

```md
On a CI runner, `rfbrowser init --with-deps chromium-headless-shell` also installs the system
packages of Chromium, which Electron needs too. On Ubuntu, the Chromium sandbox of Electron
and VS Code also needs `sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0`.
```

`--with-deps` has no effect together with `--skip-browsers`, according to Browser's code, which is why this line uses the headless shell. Playwright installs the same system packages for it as for `chromium`, because both are in the same dependency group of its registry.

### mypy follows the wheel

The wheel has types but no `py.typed`, so mypy skips it and reports 12 errors. `follow_untyped_imports = true` in the existing override for `Browser` and `Browser.*` fixes all of them (measured). `follow_imports = "silent"` and `ignore_errors` stay, so errors in Browser's own code are still not reported.

The alternative, `ignore_missing_imports` as for `robot.*`, turns `Browser` into `Any`. Strict mypy then refuses `class Electron(Browser)`, and the checks against Browser's types are gone.

### CI

- **No clone:** the repository is checked out at the root of the job's workspace. `path`, `working-directory` and the prefix of the artifact paths go away.
- **Lint job:** only `uv sync --locked` and pre-commit. All local hooks are `language: system`, and the wheel contains Browser's generated code, so neither Node nor `rfbrowser init` is needed (measured in the copy).
- **Test job:** `uv run rfbrowser init --with-deps chromium` replaces the build and `npx playwright install --with-deps chromium`. It runs before `uv run pytest`, because `test_loads_only_the_given_development_extensions` starts Browser's Node process.
- **Lock file:** `uv sync ${{ matrix.sync || '--locked' }}`. The lock file no longer follows a moving clone, so a stale lock file now fails CI.
- **Lowest versions:** the cell gets `--upgrade-package robotframework==7.1.1 --upgrade-package robotframework-browser==21.0.0`. While the lock file has Browser 21.0.0, the pin changes nothing; it takes effect when the lock file moves to a newer Browser. If the lower bound rises and the pin stays, the sync of the cell fails, so the two cannot drift apart that way.

### No job against Browser's `main`

Following `main` found the drop of Python 3.10 early, but it also turned our CI red for changes outside this repository, and its reason, the unreleased hook, is gone. New Browser versions come in through a deliberate `uv lock --upgrade-package robotframework-browser`.

The alternative, a scheduled job against `main`, can be added later without touching anything else.

### The check for the hook goes away

The libraries assume that the Browser library is installed in a suitable version, which the lower bound ensures for a normal installation. With an older Browser, `Start Electron Application` already fails in Python, because `adopted_context_options` does not exist there.

One case gets a plainer error: Browser 21 next to an older BrowserBatteries, whose Node part has no hook. A plain `pip install robotframework-electron` into a project with BrowserBatteries 20.6 produces that pair; pip reports the conflict as an error but installs anyway (measured). The start then fails with `adoptContext is not a function` and closes the application, because the call is inside the `try` that handles a failed takeover. That environment is not supported, and the documented command with `[bb]` selects matching versions (measured).

### Developer documentation

The section "Browser Library Dependency" in `AGENTS.md` shrinks to the facts above. `CONTRIBUTING.md` loses its clone steps and troubleshooting entries. `dev-docs/background.md` keeps the history in the past tense, including the fork and its remotes.

`.claude/settings.json` loses `../robotframework-browser` as an additional directory, because the setup no longer has that clone. Whoever keeps a clone for reading can add it in their personal settings.

## Risks / Trade-offs

- [A new Browser major breaks the hook, and fresh installs get it before we have tested it] → An upgrade of the lock file shows it in development. A release with an upper bound fixes it for users.
- [`rfbrowser init --with-deps` could not be tried locally, because it installs system packages with `sudo`] → It passes the option on to Playwright, as the step before did with `npx`. The first CI run checks it with `chromium`, the line in the guide with the headless shell is not run anywhere.
- [Videos cost 278 MB for 5 MB of ffmpeg] → Accepted for the guide, because the command is simple and belongs to Browser's tools. An `rfbrowser` command for ffmpeg alone would remove this; whether to ask for one is the maintainer's decision.
- [After an upgrade of Browser, the Node part in `.venv` is stale] → `uv run rfbrowser clean-node` and `uv run rfbrowser init chromium`, as Browser's own documentation says. `AGENTS.md` and `CONTRIBUTING.md` name it.

## Migration Plan

Developers run `uv sync` and `uv run rfbrowser init chromium` once. The clone at `../robotframework-browser` is no longer used and can stay for work on Browser. Nothing is published yet, so reverting the commits is the rollback.
