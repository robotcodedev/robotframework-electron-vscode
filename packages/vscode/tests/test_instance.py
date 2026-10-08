import json
from pathlib import Path

from VSCode.instance import (
    DEFAULT_SETTINGS,
    QUIET_START_ARGUMENTS,
    InstanceDirectories,
    create_instance_directories,
    instance_environment,
    launch_arguments,
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

    arguments = launch_arguments(directories, [Path("/ext/a"), Path("/ext/b")], ["--verbose"], Path("/work/space"), "linux")

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
