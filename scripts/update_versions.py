# /// script
# requires-python = ">=3.10"
# dependencies = ["commitizen>=4.19.2"]
# ///
"""Write the version that git describes into every ``pyproject.toml`` of the workspace.

A tagged commit gets the version of its tag. A later commit gets the version that
``cz bump`` would release next, as a development release:
``<next version>.dev<commits since the tag>``. ``cz bump`` sets ``CZ_PRE_NEW_VERSION``
for its hooks, which is written as it is.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def last_tag(root: Path) -> str | None:
    """Return the newest release tag in the first-parent history, or ``None`` before the first release."""
    try:
        return git(root, "describe", "--tags", "--abbrev=0", "--first-parent", "--match", "v[0-9]*")
    except subprocess.CalledProcessError:
        return None


def next_version(root: Path, current: str) -> str:
    """Return the version that ``cz bump`` would release, or the next patch version if no commit calls for one."""
    result = subprocess.run(
        [sys.executable, "-m", "commitizen", "bump", "--get-next", "--yes"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    major, minor, patch = (int(part) for part in current.split("."))
    return f"{major}.{minor}.{patch + 1}"


def git_version(root: Path) -> str:
    """Return the version of the checked-out commit."""
    tag = last_tag(root)
    commits = int(git(root, "rev-list", "--count", "--first-parent", f"{tag}..HEAD" if tag else "HEAD"))
    current = tag.removeprefix("v") if tag else "0.0.0"
    if commits == 0:
        return current
    return f"{next_version(root, current)}.dev{commits}"


def write_version(root: Path, version: str) -> None:
    """Write ``version`` into the workspace and its packages, and into the exact pins between them."""
    for pyproject in [root / "pyproject.toml", *sorted(root.glob("packages/*/pyproject.toml"))]:
        text = pyproject.read_text(encoding="utf-8")
        text = re.sub(r'^version = "[^"]*"$', f'version = "{version}"', text, count=1, flags=re.MULTILINE)
        text = re.sub(r'"(robotframework-electron)==[^"]*"', rf'"\1=={version}"', text)
        pyproject.write_text(text, encoding="utf-8")


def main() -> None:
    version = os.environ.get("CZ_PRE_NEW_VERSION") or git_version(ROOT)
    write_version(ROOT, version)
    print(version)


if __name__ == "__main__":
    main()
