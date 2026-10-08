"""Test helper for the Electron acceptance tests: the fixture app and its processes."""

import subprocess
from pathlib import Path

FIXTURE_APP = Path(__file__).resolve().parent.parent / "fixtures" / "app"


def get_fixture_app() -> str:
    """Return the path of the Electron fixture app."""
    return str(FIXTURE_APP)


def count_fixture_app_processes(marker: str) -> int:
    """Count running processes whose command line contains the fixture app path and ``marker``.

    Chromium moves switches in front of positional arguments in its command
    line, so both orders are matched.
    """
    pattern = f"{FIXTURE_APP}.*{marker}|{marker}.*{FIXTURE_APP}"
    result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    return len(result.stdout.split())
