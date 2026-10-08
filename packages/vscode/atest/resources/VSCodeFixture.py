"""Test helper for the VSCode acceptance tests: instance folders and processes."""

import subprocess
from pathlib import Path


def newest_instance_directory(output_dir: str) -> str:
    """Return the instance folder that `Open VS Code` created last in ``output_dir``."""
    base = Path(output_dir) / "vscode"
    return str(base / str(max(int(entry.name) for entry in base.iterdir() if entry.name.isdigit())))


def count_processes_with(text: str) -> int:
    """Count running processes whose command line contains ``text``."""
    result = subprocess.run(["pgrep", "-f", "--", text], capture_output=True, text=True, check=False)
    return len(result.stdout.split())


def list_user_extensions() -> list[str]:
    """Return the extension folders of the user's own VS Code."""
    folder = Path.home() / ".vscode" / "extensions"
    return sorted(entry.name for entry in folder.iterdir()) if folder.is_dir() else []
