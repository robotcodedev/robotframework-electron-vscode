import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from VSCode.instance import (
    CLI_TIMEOUT,
    DEFAULT_SETTINGS,
    QUIET_START_ARGUMENTS,
    InstanceDirectories,
    cli_environment,
    cli_path,
    create_instance_directories,
    installed_executable,
    instance_environment,
    launch_arguments,
    product_version,
    remove_instance_directories,
    run_cli,
    write_settings,
)


def test_numbers_instance_directories_per_output_directory(tmp_path):
    first = create_instance_directories(tmp_path)
    second = create_instance_directories(tmp_path)

    assert (first.root.name, second.root.name) == ("1", "2")
    assert first.user_data == tmp_path / "vscode" / "1" / "user-data"
    assert first.user_data.is_dir()
    assert first.extensions.is_dir()


def test_continues_after_the_highest_existing_number(tmp_path):
    (tmp_path / "vscode" / "7").mkdir(parents=True)

    assert create_instance_directories(tmp_path).root.name == "8"


def test_uses_a_given_extensions_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    prepared = tmp_path / "prepared"
    (prepared / "robot.test-extension-1.0.0").mkdir(parents=True)

    directories = create_instance_directories(tmp_path / "output", Path("prepared"))

    assert directories.extensions == prepared
    assert (prepared / "robot.test-extension-1.0.0").is_dir()
    assert directories.user_data == directories.root / "user-data"
    assert not (directories.root / "extensions").exists()


def test_uses_given_extensions_and_user_data_directories(tmp_path):
    extensions = tmp_path / "prepared" / "extensions"
    user_data = tmp_path / "prepared" / "user-data"

    directories = create_instance_directories(tmp_path / "output", extensions, user_data)

    assert (directories.extensions, directories.user_data) == (extensions, user_data)
    assert extensions.is_dir()
    assert user_data.is_dir()
    assert directories.root == tmp_path / "output" / "vscode" / "1"
    assert list(directories.root.iterdir()) == []


def test_uses_a_given_user_data_directory_and_a_fresh_extensions_directory(tmp_path):
    user_data = tmp_path / "prepared-user-data"

    directories = create_instance_directories(tmp_path / "output", user_data_dir=user_data)

    assert directories.user_data == user_data
    assert directories.extensions == directories.root / "extensions"
    assert directories.extensions.is_dir()


def test_uses_a_relative_user_data_directory_as_an_absolute_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    directories = create_instance_directories(tmp_path / "output", user_data_dir=Path("prepared"))

    assert directories.user_data == tmp_path / "prepared"


def test_writes_nothing_into_given_directories(tmp_path):
    extensions = tmp_path / "extensions"
    user_data = tmp_path / "user-data"
    (extensions / "robot.test-extension-1.0.0").mkdir(parents=True)
    (user_data / "User").mkdir(parents=True)
    (user_data / "User" / "settings.json").write_text('{"window.title": "prepared"}')
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    create_instance_directories(tmp_path / "output", extensions, user_data)

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if "output" not in path.parts)
    assert after == before
    assert (user_data / "User" / "settings.json").read_text() == '{"window.title": "prepared"}'


def test_writes_default_settings_overridden_by_given_settings(tmp_path):
    directories = create_instance_directories(tmp_path)

    write_settings(directories.user_data, {"window.title": "robot-test", "update.mode": "manual"})

    written = json.loads((directories.user_data / "User" / "settings.json").read_text())
    assert written == {**DEFAULT_SETTINGS, "window.title": "robot-test", "update.mode": "manual"}


def test_removes_variables_that_tie_a_process_to_a_running_vscode():
    environ = {"PATH": "/bin", "VSCODE_IPC_HOOK": "x", "VSCODE_PID": "1", "ELECTRON_RUN_AS_NODE": "1"}

    assert instance_environment(environ) == {"PATH": "/bin"}


@pytest.mark.parametrize(("system", "keeps_display"), [("linux", False), ("darwin", True), ("win32", True)])
def test_command_line_environment_has_no_display_on_linux(system, keeps_display):
    environ = {
        "PATH": "/bin",
        "DISPLAY": ":0",
        "WAYLAND_DISPLAY": "wayland-0",
        "XDG_SESSION_TYPE": "wayland",
        "VSCODE_PID": "1",
    }

    environment = cli_environment(environ, system)

    assert ("DISPLAY" in environment) is keeps_display
    assert ("WAYLAND_DISPLAY" in environment) is keeps_display
    assert ("XDG_SESSION_TYPE" in environment) is keeps_display
    assert "VSCODE_PID" not in environment


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


def test_runs_the_script_on_the_instance_directories(tmp_path, monkeypatch):
    calls = fake_cli(monkeypatch, lambda command, timeout: subprocess.CompletedProcess(command, 0, "one\ntwo\n", ""))

    output = run_cli(tmp_path / "code", instance_directories(tmp_path), ["--list-extensions"], {"NAME": "value"})

    [(command, kwargs)] = calls
    assert output == "one\ntwo\n"
    assert command == [
        str(tmp_path / "code"),
        "--list-extensions",
        "--extensions-dir",
        str(tmp_path / "extensions"),
        "--user-data-dir",
        str(tmp_path / "user-data"),
    ]
    assert kwargs["env"] == {"NAME": "value"}
    assert kwargs["timeout"] == CLI_TIMEOUT


def test_failing_script_reports_its_output(tmp_path, monkeypatch):
    fake_cli(monkeypatch, lambda command, timeout: subprocess.CompletedProcess(command, 1, "", "Not found.\n"))

    with pytest.raises(RuntimeError, match=r"^VS Code's command line failed: Not found\.$"):
        run_cli(tmp_path / "code", instance_directories(tmp_path), ["--install-extension", "unknown.ext"], {})


def test_failing_script_without_error_output_reports_its_standard_output(tmp_path, monkeypatch):
    fake_cli(monkeypatch, lambda command, timeout: subprocess.CompletedProcess(command, 1, "Failed.\n", ""))

    with pytest.raises(RuntimeError, match=r"failed: Failed\.$"):
        run_cli(tmp_path / "code", instance_directories(tmp_path), ["--update-extensions"], {})


def test_script_that_does_not_finish_is_reported(tmp_path, monkeypatch):
    def hang(command, timeout):
        raise subprocess.TimeoutExpired(command, timeout)

    fake_cli(monkeypatch, hang)

    with pytest.raises(RuntimeError, match=r"did not finish within 10 minutes: --update-extensions"):
        run_cli(tmp_path / "code", instance_directories(tmp_path), ["--update-extensions"], {})


def make_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")
    path.chmod(0o755)
    return path


@pytest.mark.parametrize(
    ("system", "executable", "cli"),
    [
        ("linux", "code", "bin/code"),
        ("linux", "code-insiders", "bin/code-insiders"),
        ("win32", "Code.exe", "bin/code.cmd"),
        (
            "darwin",
            "Visual Studio Code.app/Contents/MacOS/Code",
            "Visual Studio Code.app/Contents/Resources/app/bin/code",
        ),
    ],
)
def test_finds_command_line_script_next_to_executable(tmp_path, system, executable, cli):
    (tmp_path / cli).parent.mkdir(parents=True)
    (tmp_path / cli).touch()

    assert cli_path(tmp_path / executable, system) == tmp_path / cli


def test_reads_product_version_of_an_installation(tmp_path):
    package = tmp_path / "resources" / "app" / "package.json"
    package.parent.mkdir(parents=True)
    package.write_text(json.dumps({"version": "1.141.0"}))

    assert product_version(tmp_path / "code", "linux") == "1.141.0"
    assert product_version(tmp_path / "missing" / "code", "linux") is None


@pytest.mark.parametrize(
    ("system", "executable", "application_name", "cli"),
    [
        ("linux", "code", "code", "bin/code"),
        ("linux", "code-insiders", "code-insiders", "bin/code-insiders"),
        ("linux", "codium", "codium", "bin/codium"),
        ("linux", "cursor", "cursor", "bin/cursor"),
        ("win32", "VSCodium.exe", "codium", "bin/codium.cmd"),
        ("darwin", "VSCodium.app/Contents/MacOS/Electron", "codium", "VSCodium.app/Contents/Resources/app/bin/codium"),
    ],
)
def test_finds_command_line_script_by_product_application_name(tmp_path, system, executable, application_name, cli):
    app_folder = (
        tmp_path / "VSCodium.app" / "Contents" / "Resources" / "app"
        if system == "darwin"
        else tmp_path / "resources" / "app"
    )
    app_folder.mkdir(parents=True)
    (app_folder / "product.json").write_text(json.dumps({"applicationName": application_name}))
    (tmp_path / cli).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / cli).touch()

    assert cli_path(tmp_path / executable, system) == tmp_path / cli


def test_reports_missing_command_line_script(tmp_path):
    with pytest.raises(ValueError, match="No VS Code command-line script found"):
        cli_path(tmp_path / "codium", "linux")


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executables and symbolic links")
def test_given_executable_is_resolved_through_symbolic_links(tmp_path):
    target = make_executable(tmp_path / "VSCode-linux-x64" / "code")
    make_executable(tmp_path / "VSCode-linux-x64" / "bin" / "code")
    link = tmp_path / "links" / "code"
    link.parent.mkdir()
    link.symlink_to(target)

    executable = installed_executable(link)

    assert executable == target.resolve()
    assert cli_path(executable, "linux") == target.resolve().parent / "bin" / "code"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executables")
def test_given_executable_is_found_on_path(tmp_path, monkeypatch):
    target = make_executable(tmp_path / "bin" / "my-code")
    monkeypatch.setenv("PATH", str(target.parent))

    assert installed_executable(Path("my-code")) == target.resolve()


def test_missing_executable_is_reported(tmp_path):
    with pytest.raises(ValueError, match=r"VS Code executable '.*missing-code' not found"):
        installed_executable(tmp_path / "missing-code")
