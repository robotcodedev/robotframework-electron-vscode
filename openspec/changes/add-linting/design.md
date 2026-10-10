# Design

## Context

See proposal.md for motivation. Findings from 2026-10-10, with ruff 0.17, mypy 2.4 and pre-commit 4.6:
- **robotframework-platynui** runs Ruff's default rule set plus further families, Google-style docstrings, mypy in strict mode, and pre-commit with standard hooks, Conventional Commits and local ruff and mypy hooks. It formats with single quotes.
- **First run with a platynui-like configuration:** ruff found 24 issues, `ruff format` would reformat 5 files, and mypy in strict mode found 17 errors in the sources, most of them from robotlibcore's untyped `keyword` decorator.
- **Duplicate test modules:** both packages have `tests/test_helper.py` and `tests/test_library.py` without `__init__.py`. pytest imports them with `--import-mode=importlib`, but mypy reports duplicate modules.
- **Browser for mypy:** the Browser clone is installed through setuptools' editable import hook, which mypy cannot follow, and Browser has no `py.typed`. Its generated `browser.pyi` has untyped definitions.

## Goals / Non-Goals

**Goals:**
- One set of checks that runs the same in the editor, before a commit and on CI.
- Strict typing of the libraries' sources, with Browser's real types.

**Non-Goals:**
- Robot Framework formatting with Robocop. RobotCode's analysis covers the Robot Framework files.
- A pre-push gate. CI runs the full checks.

## Decisions

- **Ruff like platynui, with double quotes.** Line length 120, Ruff's default rules plus `E`, `F`, `W`, `I`, `N`, `YTT`, `DTZ`, `T10`, `ISC`, `G`, `PIE`, `PT`, `Q`, `RET`, `RSE` and `RUF`, Google-style docstrings, target Python 3.10. Quotes stay double, as in the existing code and the Browser library, so formatting changes only a few files.
- **mypy strict for the sources, with relaxed annotations for tests.** Tests need no annotations on every test function, but `check_untyped_defs` checks their bodies. `disallow_untyped_decorators` is off because of robotlibcore's `keyword`.
- **Module names relative to the repository root.** `explicit_package_bases` with `mypy_path` set to the two `src` folders and the repository root: the sources keep their import names `Electron` and `VSCode`, and the tests become `packages.electron.tests.test_helper` and so on, so they no longer collide.
- **Browser through the clone's path.** The clone is on `mypy_path` until Browser is released with the hook, with `follow_imports = "silent"` and `ignore_errors = true` for `Browser.*`: our code gets Browser's types, Browser's own code is not reported.
- **Hooks through `uv run`.** The local hooks run the project's own ruff, mypy and RobotCode from the workspace, so the versions match `uv.lock`, and mypy sees the installed packages. Standard hooks and Conventional Commits come from their pre-commit repositories.
- **A lint job before the tests on CI.** It checks out the Browser clone for mypy, without building it, and runs `pre-commit run --all-files` with the commit-msg hook left out. The test job needs it.

## Risks / Trade-offs

- [`mypy_path` points outside the repository] → It matches the editable path source in `pyproject.toml`, and both go when Browser is released with the hook.
- [A Ruff upgrade can widen the default rule set] → New findings are triaged and fixed or ignored with a comment.
