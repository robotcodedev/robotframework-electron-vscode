"""Directories, settings, environment and arguments of isolated VS Code instances."""

import json
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


def create_instance_directories(output_dir: Path) -> InstanceDirectories:
    """Create the next numbered instance folder ``<output_dir>/vscode/<n>``."""
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
    directories = InstanceDirectories(root.absolute(), root.absolute() / "user-data", root.absolute() / "extensions")
    (directories.user_data / "User").mkdir(parents=True)
    directories.extensions.mkdir()
    return directories


def write_settings(user_data: Path, settings: Mapping[str, Any] | None) -> dict[str, Any]:
    """Write the default settings, overridden by ``settings``, as the instance's user settings."""
    merged = {**DEFAULT_SETTINGS, **(settings or {})}
    (user_data / "User" / "settings.json").write_text(json.dumps(merged, indent=4), encoding="utf-8")
    return merged


def instance_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Return ``environ`` without the variables that tie a process to a running VS Code."""
    return {key: value for key, value in environ.items() if not key.startswith("VSCODE_") and key != "ELECTRON_RUN_AS_NODE"}


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


def install_extension(cli: Path, extension: str, directories: InstanceDirectories, env: Mapping[str, str]) -> None:
    """Install a Marketplace extension or a ``.vsix`` file into the instance's extensions directory."""
    result = subprocess.run(
        [
            str(cli),
            "--install-extension",
            extension,
            "--extensions-dir",
            str(directories.extensions),
            "--user-data-dir",
            str(directories.user_data),
        ],
        env=dict(env),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Installing extension '{extension}' failed: {(result.stderr or result.stdout).strip()}")
