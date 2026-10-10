# Proposal

## Why

Both packages carry a hand-written version, 0.1.0, and the repository has no changelog. Before the first release, the version and the changelog should come from the history the way robotframework-platynui does it: the Conventional Commits decide the next version, a tag marks each release, and the changelog is generated from the commits. Wheels that CI builds between releases should carry a development version of their own, so that they cannot be mistaken for a release.

## What Changes

- commitizen makes releases with `cz bump`: it determines the next version from the commits since the last tag, writes it into the packages, regenerates the changelog, commits and creates a signed, annotated tag `v<version>`.
- git-cliff generates `CHANGELOG.md` from the Conventional Commits, grouped into features, bug fixes, documentation, performance and refactoring.
- A script writes the version that git describes into every `pyproject.toml`: the tag's version on a tagged commit, and `<next version>.dev<commits since the tag>` after it. `robotframework-vscode` requires exactly the `robotframework-electron` of its own version.
- The CI build job writes the version from git before it builds the wheels.
- The contribution guide and AGENTS.md describe versions, the changelog and releases.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The change adds release tooling and changes no behaviour of the libraries.

## Impact

- `pyproject.toml` (dev dependencies, `[tool.commitizen]`), `packages/*/pyproject.toml`, `uv.lock`.
- New `cliff.toml`, `CHANGELOG.md` and `scripts/update_versions.py`.
- `.github/workflows/ci.yml`, `CONTRIBUTING.md` and `AGENTS.md`.
