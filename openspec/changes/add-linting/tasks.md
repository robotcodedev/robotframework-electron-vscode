# Tasks

## 1. Configuration

- [x] 1.1 Add ruff, mypy and pre-commit as dev dependencies, and `[tool.ruff]` and `[tool.mypy]` to the root `pyproject.toml`.
- [x] 1.2 Add `.pre-commit-config.yaml` with the standard hooks, Conventional Commits for commit messages, and local hooks for `ruff check`, `ruff format --check`, mypy and RobotCode's analysis of the repository and the example.

## 2. Findings

- [x] 2.1 Fix the ruff findings and format the Python files with `ruff format`.
- [x] 2.2 Fix the mypy findings. Verify that `uv run pytest`, `uv run pre-commit run --all-files` and the acceptance tests pass.

## 3. CI and documentation

- [x] 3.1 Add a lint job to `.github/workflows/ci.yml` that runs the pre-commit checks, and let the test job need it.
- [x] 3.2 Describe the checks and the pre-commit hooks in `CONTRIBUTING.md` and the commands in `AGENTS.md`.
