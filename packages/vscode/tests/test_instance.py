import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from VSCode.instance import (
    DEFAULT_SETTINGS,
    INSTALL_TIMEOUT,
    QUIET_START_ARGUMENTS,
    InstanceDirectories,
    create_instance_directories,
    install_extensions,
    instance_environment,
    launch_arguments,
    remove_instance_directories,
    write_settings,
)


def test_numbers_instance_directories_per_output_directory(tmp_path):
    first = create_instance_directories(tmp_path)
    second = create_instance_directories(tmp_path)

    assert (first.root.name, second.root.name) == ("1", "2")
    assert first.user_data == tmp_path / "vscode" / "1" / "user-data"
    assert (first.user_data / "User").is_dir()
    assert first.extensions.is_dir()


def test_continues_after_the_highest_existing_number(tmp_path):
    (tmp_path / "vscode" / "7").mkdir(parents=True)

    assert create_instance_directories(tmp_path).root.name == "8"


def test_writes_default_settings_overridden_by_given_settings(tmp_path):
    directories = create_instance_directories(tmp_path)

    write_settings(directories.user_data, {"window.title": "robot-test", "update.mode": "manual"})

    written = json.loads((directories.user_data / "User" / "settings.json").read_text())
    assert written == {**DEFAULT_SETTINGS, "window.title": "robot-test", "update.mode": "manual"}


def test_removes_variables_that_tie_a_process_to_a_running_vscode():
    environ = {"PATH": "/bin", "VSCODE_IPC_HOOK": "x", "VSCODE_PID": "1", "ELECTRON_RUN_AS_NODE": "1"}

    assert instance_environment(environ) == {"PATH": "/bin"}


def test_launch_arguments_isolate_the_instance_and_open_the_path_last(tmp_path):
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")

    arguments = launch_arguments(
        directories, [Path("/ext/a"), Path("/ext/b")], ["--verbose"], Path("/work/space"), "linux"
    )

    assert arguments == [
        f"--user-data-dir={tmp_path / 'user-data'}",
        f"--extensions-dir={tmp_path / 'extensions'}",
        "--extensionDevelopmentPath=/ext/a",
        "--extensionDevelopmentPath=/ext/b",
        *QUIET_START_ARGUMENTS,
        "--disable-dev-shm-usage",
        "--verbose",
        "/work/space",
    ]


def test_launch_arguments_without_path_and_outside_linux(tmp_path):
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")

    arguments = launch_arguments(directories, [], [], None, "win32")

    assert "--disable-dev-shm-usage" not in arguments
    assert arguments[-1] == QUIET_START_ARGUMENTS[-1]


def test_removes_only_the_instance_directories(tmp_path):
    create_instance_directories(tmp_path)
    create_instance_directories(tmp_path)
    (tmp_path / "output.xml").write_text("<robot/>")
    (tmp_path / "browser").mkdir()

    remove_instance_directories(tmp_path)

    assert sorted(entry.name for entry in tmp_path.iterdir()) == ["browser", "output.xml"]


def test_removing_without_instance_directories_is_fine(tmp_path):
    remove_instance_directories(tmp_path)

    assert list(tmp_path.iterdir()) == []


def fake_cli(
    monkeypatch: pytest.MonkeyPatch, outcome: Callable[[list[str], float], subprocess.CompletedProcess[str]]
) -> list[tuple[list[str], dict[str, Any]]]:
    """Replaces the command-line script's run with ``outcome(command, timeout)`` and records the calls."""
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return outcome(command, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def instance_directories(root: Path) -> InstanceDirectories:
    return InstanceDirectories(root, root / "user-data", root / "extensions")


def test_installs_all_extensions_with_one_call(tmp_path, monkeypatch):
    calls = fake_cli(monkeypatch, lambda command, timeout: subprocess.CompletedProcess(command, 0, "", ""))
    directories = instance_directories(tmp_path)

    install_extensions(tmp_path / "code", ["ms-python.python", "extension.vsix"], directories, {"NAME": "value"})

    [(command, kwargs)] = calls
    assert command == [
        str(tmp_path / "code"),
        "--install-extension",
        "ms-python.python",
        "--install-extension",
        "extension.vsix",
        "--extensions-dir",
        str(directories.extensions),
        "--user-data-dir",
        str(directories.user_data),
    ]
    assert kwargs["env"] == {"NAME": "value"}
    assert kwargs["timeout"] == INSTALL_TIMEOUT == 600


def test_installation_that_does_not_finish_names_the_extensions(tmp_path, monkeypatch):
    def hang(command, timeout):
        raise subprocess.TimeoutExpired(command, timeout)

    fake_cli(monkeypatch, hang)

    with pytest.raises(RuntimeError, match=r"extensions 'one', 'two' did not finish within 10 minutes"):
        install_extensions(tmp_path / "code", ["one", "two"], instance_directories(tmp_path), {})


def test_failed_installation_reports_the_output_of_the_script(tmp_path, monkeypatch):
    fake_cli(monkeypatch, lambda command, timeout: subprocess.CompletedProcess(command, 1, "", "Not found.\n"))

    with pytest.raises(RuntimeError, match=r"^Installing extension 'unknown.ext' failed: Not found\.$"):
        install_extensions(tmp_path / "code", ["unknown.ext"], instance_directories(tmp_path), {})
