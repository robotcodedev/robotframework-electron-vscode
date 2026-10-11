"""Directories, settings, environment and arguments of isolated VS Code instances."""

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

DEFAULT_SETTINGS: dict[str, Any] = {
    "workbench.startupEditor": "none",
    "update.mode": "none",
    "telemetry.telemetryLevel": "off",
    "extensions.autoUpdate": False,
    "extensions.autoCheckUpdates": False,
    "security.workspace.trust.enabled": False,
    # Under Playwright, VS Code detects a screen reader and changes the editor's behaviour.
    "editor.accessibilitySupport": "off",
    "workbench.secondarySideBar.defaultVisibility": "hidden",
}

# Seconds for one call of the command-line script, enough for large extensions on a slow CI runner.
CLI_TIMEOUT = 600

QUIET_START_ARGUMENTS = [
    "--skip-welcome",
    "--skip-release-notes",
    "--disable-telemetry",
    "--disable-updates",
    "--disable-workspace-trust",
]


class InstanceDirectories(NamedTuple):
    root: Path
    user_data: Path
    extensions: Path


def create_instance_directories(output_dir: Path, extensions_dir: Path | None = None) -> InstanceDirectories:
    """Create the next numbered instance folder ``<output_dir>/vscode/<n>``.

    With ``extensions_dir``, the instance uses that extensions directory instead of one in its folder.
    """
    base = output_dir / "vscode"
    base.mkdir(parents=True, exist_ok=True)
    number = 1 + max((int(entry.name) for entry in base.iterdir() if entry.name.isdigit()), default=0)
    while True:
        root = base / str(number)
        try:
            root.mkdir()
            break
        except FileExistsError:
            number += 1
    extensions = Path(os.path.abspath(extensions_dir)) if extensions_dir else root.absolute() / "extensions"
    directories = InstanceDirectories(root.absolute(), root.absolute() / "user-data", extensions)
    (directories.user_data / "User").mkdir(parents=True)
    directories.extensions.mkdir(parents=True, exist_ok=True)
    return directories


def remove_instance_directories(output_dir: Path) -> None:
    """Remove ``<output_dir>/vscode``, the instance folders of earlier runs."""
    shutil.rmtree(output_dir / "vscode", ignore_errors=True)


def write_settings(user_data: Path, settings: Mapping[str, Any] | None) -> dict[str, Any]:
    """Write the default settings, overridden by ``settings``, as the instance's user settings."""
    merged = {**DEFAULT_SETTINGS, **(settings or {})}
    (user_data / "User" / "settings.json").write_text(json.dumps(merged, indent=4), encoding="utf-8")
    return merged


def instance_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Return ``environ`` without the variables that tie a process to a running VS Code."""
    return {
        key: value for key, value in environ.items() if not key.startswith("VSCODE_") and key != "ELECTRON_RUN_AS_NODE"
    }


def launch_arguments(
    directories: InstanceDirectories,
    development_paths: Sequence[Path],
    extra_args: Sequence[str],
    path: Path | None,
    system: str = sys.platform,
) -> list[str]:
    """Return the command-line arguments of an isolated instance."""
    arguments = [f"--user-data-dir={directories.user_data}", f"--extensions-dir={directories.extensions}"]
    arguments += [f"--extensionDevelopmentPath={Path(extension).absolute()}" for extension in development_paths]
    arguments += QUIET_START_ARGUMENTS
    if system == "linux":
        arguments.append("--disable-dev-shm-usage")
    arguments += extra_args
    if path is not None:
        arguments.append(str(Path(path).absolute()))
    return arguments


# Options that would name other directories than the ones run_cli is given.
DIRECTORY_OPTIONS = ("--extensions-dir", "--user-data-dir")


def run_cli(cli: Path, extensions_dir: Path, user_data_dir: Path, args: Sequence[str], env: Mapping[str, str]) -> str:
    """Run the command-line script with ``args`` on the given directories and return its output."""
    for arg in args:
        if arg.split("=", 1)[0] in DIRECTORY_OPTIONS:
            raise ValueError(f"Give the directories as the keyword's arguments, not as '{arg}'.")
    command = [str(cli), *args]
    command += ["--extensions-dir", os.path.abspath(extensions_dir), "--user-data-dir", os.path.abspath(user_data_dir)]
    try:
        result = subprocess.run(
            command, env=dict(env), capture_output=True, text=True, check=False, timeout=CLI_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"VS Code's command line did not finish within {CLI_TIMEOUT // 60} minutes: {' '.join(args)}"
        ) from None
    if result.returncode != 0:
        raise RuntimeError(f"VS Code's command line failed: {(result.stderr or result.stdout).strip()}")
    return result.stdout
