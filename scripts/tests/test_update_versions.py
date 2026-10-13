import os
import shutil
import subprocess
from pathlib import Path

import pytest
from packaging.version import Version

from scripts.update_versions import HELPER_MANIFEST, git_version, semantic_version, write_version

ROOT = Path(__file__).resolve().parents[2]
PYPROJECTS = ["pyproject.toml", "packages/electron/pyproject.toml", "packages/vscode/pyproject.toml"]
FILES = [*PYPROJECTS, HELPER_MANIFEST.as_posix()]


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def commit(repo: Path, message: str) -> None:
    git(repo, "commit", "--allow-empty", "-m", message)


def tag(repo: Path, name: str) -> None:
    git(repo, "tag", "-a", name, "-m", name)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A git repository with the workspace's versioned files, outside the user's git configuration."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for variable in ("GIT_AUTHOR", "GIT_COMMITTER"):
        monkeypatch.setenv(f"{variable}_NAME", "Robot")
        monkeypatch.setenv(f"{variable}_EMAIL", "robot@example.org")
    repo = tmp_path / "repo"
    for name in FILES:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, repo / name)
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    commit(repo, "build: set up the workspace")
    return repo


def test_tagged_commit_has_the_version_of_its_tag(repo):
    commit(repo, "feat(electron): add New Electron Application")
    tag(repo, "v0.1.0")

    assert git_version(repo) == "0.1.0"


def test_feature_after_a_release_raises_the_minor_version(repo):
    tag(repo, "v0.1.0")
    commit(repo, "feat(vscode): add Open VS Code")
    commit(repo, "fix(vscode): keep the original error")

    assert git_version(repo) == "0.2.0.dev2"


def test_fix_after_a_release_raises_the_patch_version(repo):
    tag(repo, "v0.1.0")
    commit(repo, "fix(electron): close the application when the start fails")

    assert git_version(repo) == "0.1.1.dev1"


def test_breaking_change_raises_the_minor_version_while_the_major_version_is_zero(repo):
    tag(repo, "v0.1.0")
    commit(repo, "feat(electron)!: rename New Electron Application")

    assert git_version(repo) == "0.2.0.dev1"


def test_commits_that_call_for_no_version_raise_the_patch_version(repo):
    tag(repo, "v0.1.0")
    commit(repo, "ci: lint before the tests")

    assert git_version(repo) == "0.1.1.dev1"


def test_without_a_tag_the_commits_count_from_the_first_one(repo):
    commit(repo, "feat(electron): add New Electron Application")
    commit(repo, "docs: add a guide")

    assert git_version(repo) == "0.1.0.dev3"


def test_writes_the_version_into_every_pyproject_and_the_pin(repo):
    write_version(repo, "0.2.0.dev3")

    texts = {name: (repo / name).read_text(encoding="utf-8") for name in PYPROJECTS}
    assert all('\nversion = "0.2.0.dev3"\n' in text for text in texts.values())
    assert 'name = "robotframework-electron"\n' in texts["packages/electron/pyproject.toml"]
    assert '"robotframework-electron==0.2.0.dev3"' in texts["packages/vscode/pyproject.toml"]


def test_writes_the_version_into_the_helper_extension_as_a_semantic_version(repo):
    write_version(repo, "0.2.0.dev3")

    assert '"version": "0.2.0-dev.3",' in (repo / HELPER_MANIFEST).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("version", "expected"),
    [("0.2.0", "0.2.0"), ("0.2.0.dev12", "0.2.0-dev.12"), ("0.2.0rc1", "0.2.0-rc.1"), ("0.2.0a1", "0.2.0-a.1")],
)
def test_semantic_version_reads_as_the_same_version(version, expected):
    assert semantic_version(version) == expected
    assert Version(semantic_version(version)) == Version(version)
