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


def create_instance_directories(
    output_dir: Path, extensions_dir: Path | None = None, user_data_dir: Path | None = None
) -> InstanceDirectories:
    """Create the next numbered instance folder ``<output_dir>/vscode/<n>``.

    A given ``extensions_dir`` or ``user_data_dir`` is used in place, as an absolute path, and only created
    if it does not exist. The directories that are not given are created fresh in the instance folder.
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
    root = Path(os.path.abspath(root))
    directories = InstanceDirectories(
        root,
        Path(os.path.abspath(user_data_dir or root / "user-data")),
        Path(os.path.abspath(extensions_dir or root / "extensions")),
    )
    directories.user_data.mkdir(parents=True, exist_ok=True)
    directories.extensions.mkdir(parents=True, exist_ok=True)
    return directories


def _app_folder(executable: Path, system: str) -> Path:
    if system == "darwin":
        return executable.parents[1] / "Resources" / "app"
    return executable.parent / "resources" / "app"


def _application_name(executable: Path, system: str) -> str | None:
    """Return the ``applicationName`` from the build's ``product.json``, such as ``codium`` for VSCodium."""
    product = _app_folder(executable, system) / "product.json"
    try:
        return str(json.loads(product.read_text(encoding="utf-8"))["applicationName"])
    except (OSError, ValueError, KeyError):
        return None


def installed_executable(executable: Path) -> Path:
    """Return the file that ``executable`` names, also as a command on ``PATH`` or through symbolic links."""
    found = shutil.which(str(executable))
    if found is None:
        raise ValueError(f"VS Code executable '{executable}' not found.")
    return Path(found).resolve()


def cli_path(executable: Path, system: str = sys.platform) -> Path:
    """Return the command-line script that belongs to ``executable``, also for forks of VS Code."""
    bin_dir = _app_folder(executable, system) / "bin" if system == "darwin" else executable.parent / "bin"
    suffix = ".cmd" if system == "win32" else ""
    names = dict.fromkeys(name for name in (_application_name(executable, system), "code", "code-insiders") if name)
    for name in names:
        if (bin_dir / f"{name}{suffix}").is_file():
            return bin_dir / f"{name}{suffix}"
    raise ValueError(f"No VS Code command-line script found in {bin_dir}.")


def product_version(executable: Path, system: str = sys.platform) -> str | None:
    """Return the version of the VS Code that ``executable`` belongs to, if it can be found."""
    package = _app_folder(executable, system) / "package.json"
    try:
        return str(json.loads(package.read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return None


def remove_instance_directories(output_dir: Path) -> None:
    """Remove ``<output_dir>/vscode``, the instance folders of earlier runs."""
    shutil.rmtree(output_dir / "vscode", ignore_errors=True)


def write_settings(user_data: Path, settings: Mapping[str, Any] | None) -> None:
    """Write the default settings, overridden by ``settings``, as the instance's user settings."""
    file = user_data / "User" / "settings.json"
    file.parent.mkdir(exist_ok=True)
    file.write_text(json.dumps({**DEFAULT_SETTINGS, **(settings or {})}, indent=4), encoding="utf-8")


def instance_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Return ``environ`` without the variables that tie a process to a running VS Code."""
    return {
        key: value for key, value in environ.items() if not key.startswith("VSCODE_") and key != "ELECTRON_RUN_AS_NODE"
    }


def cli_environment(environ: Mapping[str, str], system: str = sys.platform) -> dict[str, str]:
    """Return the environment for VS Code's command-line script: an instance's, and on Linux without a display.

    Without a command, the script starts VS Code's window instead; without a display, no window can open. With
    ``XDG_SESSION_TYPE=wayland``, VS Code would connect to the default Wayland socket ``wayland-0`` even without
    ``WAYLAND_DISPLAY``.
    """
    environment = instance_environment(environ)
    if system == "linux":
        for name in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE"):
            environment.pop(name, None)
    return environment


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


# Options of the command-line script that would name other directories than the instance's.
DIRECTORY_OPTIONS = ("--extensions-dir", "--user-data-dir")


def run_cli(cli: Path, directories: InstanceDirectories, args: Sequence[str], env: Mapping[str, str]) -> str:
    """Run the command-line script with ``args`` on an instance's directories and return its output."""
    command = [str(cli), *args]
    command += ["--extensions-dir", str(directories.extensions), "--user-data-dir", str(directories.user_data)]
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
