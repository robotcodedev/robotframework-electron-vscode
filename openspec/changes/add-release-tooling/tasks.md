# Tasks

## 1. Versions

- [x] 1.1 Add commitizen and git-cliff as dev dependencies and `[tool.commitizen]` to the root `pyproject.toml`.
- [x] 1.2 Add `scripts/update_versions.py`, which writes the version from git into every `pyproject.toml` and pins `robotframework-electron` in `robotframework-vscode`. Add unit tests for the version from a tag, after a tag and without a tag.

## 2. Changelog

- [x] 2.1 Add `cliff.toml` and generate `CHANGELOG.md`.

## 3. CI and documentation

- [x] 3.1 Let the CI build job fetch the history with tags and write the version before it builds the wheels.
- [x] 3.2 Describe versions, the changelog and releases in `CONTRIBUTING.md` and the commands in `AGENTS.md`.
- [x] 3.3 Verify with `cz bump --dry-run`, `uv run pytest` and `uv run pre-commit run --all-files`.
