# Proposal

## Why

The repository has no linter, no type checker and no commit hooks. Style, imports and types are checked by hand in review, and the contribution guide promises checks it cannot point to. Before the libraries grow further, the Python code should be checked the way RobotCode and robotframework-platynui do it, and the checks should run before every commit and on CI.

## What Changes

- ruff checks and formats the Python code of the packages, their tests, the example and the documentation scripts, with a configuration modelled on robotframework-platynui's: line length 120, Ruff's default rules plus further rule families, docstrings in Google style, and double quotes like the existing code and the Browser library.
- mypy checks the packages and their tests in strict mode.
- A pre-commit configuration runs standard hooks (large files, TOML and YAML, end of file, trailing whitespace), ruff, mypy and RobotCode's static analysis of the Robot Framework files, and checks commit messages against Conventional Commits.
- The CI workflow gets a lint job that runs the same checks before the tests.
- The existing findings are fixed, and the contribution guide and AGENTS.md describe the checks.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The change adds development tooling and changes no behaviour of the libraries.

## Impact

- `pyproject.toml` (dev dependencies, `[tool.ruff]`, `[tool.mypy]`), a new `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
- Formatting and small fixes in the Python sources and tests.
- `CONTRIBUTING.md` and `AGENTS.md`.
