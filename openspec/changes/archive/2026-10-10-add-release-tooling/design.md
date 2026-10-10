# Design

## Context

See proposal.md for motivation. Findings from 2026-10-10:
- **robotframework-platynui** releases with commitizen (`cz bump`, `version_provider = "scm"`, tags `v<version>`, `major_version_zero`, signed annotated tags). Its `pre_bump_hooks` write the version into all manifests with `scripts/update-git-versions.py` and regenerate `CHANGELOG.md` with git-cliff through `scripts/update-changelog.py`. CI runs the version script before it builds wheels, so that each commit after a tag gets `<next version>-dev.<commits>`. The scripts use gitpython and semantic-version, and the next version is computed by rules of their own.
- **This repository** has no tags yet. The two packages and the virtual workspace root have the version 0.1.0 in their `pyproject.toml`, and `__version__` comes from the installed metadata. `robotframework-vscode` requires `robotframework-electron` without a version, although it builds on Electron's internals (`Electron._docs`, `Electron.Helper`).
- **git-cliff** is on PyPI as wheels for Linux, macOS and Windows, so it can be a dev dependency instead of a Rust tool.

## Goals / Non-Goals

**Goals:**
- One version for both packages, decided by the Conventional Commits and set by a tag.
- A changelog that is generated, not written by hand.
- Wheels from CI that say which commit they come from.

**Non-Goals:**
- Publishing to PyPI or creating GitHub releases. That follows once Browser has released the hook.
- Separate versions per package.

## Decisions

- **commitizen with versions from tags.** `version_provider = "scm"`, `tag_format = "v$version"`, `version_scheme = "pep440"` (only Python packages, unlike platynui's semver2 for Cargo), `major_version_zero = true` while the project is 0.x, and signed annotated tags. `update_changelog_on_bump = false`, because git-cliff writes the changelog.
- **Pre-bump hooks.** `cz bump` runs `scripts/update_versions.py`, then git-cliff with the new tag, then `uv lock --offline`, and stages exactly the files they change. commitizen sets `CZ_PRE_NEW_VERSION` for the hooks.
- **One script for the version.** `scripts/update_versions.py` takes `CZ_PRE_NEW_VERSION` if it is set, and otherwise derives the version from `git describe --tags --first-parent --match 'v[0-9]*'`: a tagged commit gets the tag's version, a later commit `<next version>.dev<commits since the tag>`. The next version comes from `cz bump --get-next`, so it follows exactly the rules of the release; when no commit calls for a new version, the patch version is raised, so that the development version still sorts after the release. Without any tag, the count starts at the first commit. The script is a PEP 723 script with commitizen as its only dependency, so `uv run scripts/update_versions.py` runs without the workspace and its Browser clone. Only the standard library and git otherwise, no gitpython.
- **One version, exact pin.** The script writes the version into the root `pyproject.toml` and both packages, and pins `robotframework-electron==<version>` in `robotframework-vscode`.
- **git-cliff configuration like platynui's.** The same template and groups, with links to this repository. `docs(openspec)` commits are left out, because they plan work rather than change what users get, as are `chore`, `ci`, `build`, `style` and `test`.
- **CI.** The build job checks out the full history with tags and runs the version script before `uv build`. The changelog is not regenerated on CI.

## Risks / Trade-offs

- [`cz bump --get-next` fails when no commit calls for a version] → The script falls back to the next patch version.
- [The exact pin makes the two packages installable only together at one version] → They are released together, and VSCode uses Electron's internals.
- [A wheel built locally carries the committed version, not the development version] → Only CI builds wheels for others, and it writes the version first.
