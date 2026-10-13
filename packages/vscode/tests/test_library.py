import inspect
import sys
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path
from typing import Any

import pytest
from Browser import playwright
from Browser.utils.data_types import AutoClosingLevel, ColorScheme
from robot.running.testlibraries import TestLibrary as RobotLibrary

import VSCode
from Electron import HIDDEN_KEYWORDS, Electron
from VSCode import Instance
from VSCode.extension_host import PAGE_WORKSPACE_ID, PageNotReadyError, UnknownWorkspaceError
from VSCode.instance import DEFAULT_SETTINGS, InstanceDirectories


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


def import_library(*args: str):
    return RobotLibrary.from_name("VSCode", args=list(args)).instance


def test_contains_every_electron_and_browser_keyword():
    vscode = import_library()

    assert set(Electron().get_keyword_names()) <= set(vscode.get_keyword_names())


def test_hides_the_keywords_that_electron_hides():
    assert not set(import_library().get_keyword_names()) & HIDDEN_KEYWORDS


def test_adds_only_its_own_keywords_to_electron():
    added = set(import_library().get_keyword_names()) - set(Electron().get_keyword_names())

    assert added == {
        "Start VS Code",
        "Close VS Code",
        "Get VS Code Instance Directories",
        "Execute VS Code CLI Command",
        "Evaluate In Extension Host",
    }


def test_instance_directories_of_the_active_instance(monkeypatch, tmp_path):
    vscode = import_library()
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "prepared")
    vscode._instances()["browser=open"] = Instance(tmp_path / "code", directories)

    result = vscode.get_vs_code_instance_directories()

    assert result == {
        "root": str(tmp_path),
        "user_data": str(tmp_path / "user-data"),
        "extensions": str(tmp_path / "prepared"),
    }
    assert result.extensions == str(tmp_path / "prepared")


def test_instance_directories_of_a_browser_not_started_by_start_vs_code_fail():
    with pytest.raises(ValueError, match="'browser=unknown' is not an open VS Code instance"):
        import_library().get_vs_code_instance_directories("browser=unknown")


def test_instance_directories_without_an_open_instance_fail(monkeypatch):
    vscode = import_library()
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: [])

    with pytest.raises(ValueError, match=r"^No VS Code instance is open\.$"):
        vscode.get_vs_code_instance_directories()


def test_instance_directories_of_a_closed_instance_fail(monkeypatch, tmp_path):
    vscode = import_library()
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")
    instances = vscode._instances()
    instances["browser=open"] = instances["browser=closed"] = Instance(tmp_path / "code", directories)

    with pytest.raises(ValueError, match="'browser=closed' is not an open VS Code instance"):
        vscode.get_vs_code_instance_directories("browser=closed")
    assert list(vscode._instances()) == ["browser=open"]


def test_keeps_the_error_of_the_workbench_when_closing_fails(monkeypatch, tmp_path):
    executable = tmp_path / "code"
    executable.write_text("")
    executable.chmod(0o755)
    vscode = import_library()
    vscode.outputdir = str(tmp_path / "output")

    def not_ready(*args, **kwargs):
        raise TimeoutError("workbench not ready")

    def close_fails(*args, **kwargs):
        raise RuntimeError("closing failed")

    monkeypatch.setattr(vscode, "start_electron_application", lambda *args, **kwargs: ("browser", {}))
    monkeypatch.setattr(vscode, "wait_for_elements_state", not_ready)
    monkeypatch.setattr(vscode, "close_browser", close_fails)

    with pytest.raises(TimeoutError, match="workbench not ready"):
        vscode.start_vs_code(executable)
    assert vscode._instances() == {}


def recording_start(monkeypatch, tmp_path) -> tuple[Any, Path, dict[str, Any]]:
    """Imports the library with a fake start that records the arguments of `Start Electron Application`."""
    executable = tmp_path / "code"
    executable.write_text("")
    executable.chmod(0o755)
    vscode = import_library()
    vscode.outputdir = str(tmp_path / "output")
    started: dict[str, Any] = {}

    def start_electron_application(*args, **kwargs):
        started.update(kwargs)
        return ("browser", {})

    monkeypatch.setattr(vscode, "start_electron_application", start_electron_application)
    monkeypatch.setattr(vscode, "wait_for_elements_state", lambda *args, **kwargs: None)
    return vscode, executable, started


def test_passes_the_launch_options_on(monkeypatch, tmp_path):
    vscode, executable, started = recording_start(monkeypatch, tmp_path)

    vscode.start_vs_code(
        executable,
        color_scheme=ColorScheme.dark,
        locale="pt-BR",
        timezone_id="Asia/Tokyo",
        bypass_csp=True,
    )

    assert {key: started[key] for key in ("color_scheme", "locale", "timezone_id", "bypass_csp")} == {
        "color_scheme": ColorScheme.dark,
        "locale": "pt-BR",
        "timezone_id": "Asia/Tokyo",
        "bypass_csp": True,
    }


def development_paths(arguments: list[str]) -> list[str]:
    return [arg.split("=", 1)[1] for arg in arguments if arg.startswith("--extensionDevelopmentPath=")]


def test_loads_only_the_given_development_extensions(monkeypatch, tmp_path):
    vscode, executable, started = recording_start(monkeypatch, tmp_path)

    vscode.start_vs_code(executable)
    without = development_paths(started["args"])
    vscode.start_vs_code(executable, extension_development_path=tmp_path / "extension")

    assert without == []
    assert development_paths(started["args"]) == [str(tmp_path / "extension")]


def test_starts_with_a_given_user_data_directory_and_writes_no_settings_into_it(monkeypatch, tmp_path):
    vscode, executable, started = recording_start(monkeypatch, tmp_path)
    prepared = tmp_path / "prepared"
    prepared.mkdir()

    vscode.start_vs_code(executable, user_data_dir=prepared)

    assert f"--user-data-dir={prepared}" in started["args"]
    assert list(prepared.iterdir()) == []


def test_settings_with_a_given_user_data_directory_fail_before_the_start(monkeypatch, tmp_path):
    vscode, executable, started = recording_start(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match=r"^'settings' cannot be combined with 'user_data_dir'"):
        vscode.start_vs_code(executable, user_data_dir=tmp_path / "prepared", settings={"window.title": "x"})
    assert started == {}
    assert not (tmp_path / "output").exists()
    assert not (tmp_path / "prepared").exists()


def test_documents_every_default_setting():
    documentation = VSCode.VSCode.start_vs_code.__doc__ or ""

    assert all(f"``{name}: " in documentation for name in DEFAULT_SETTINGS)


def test_converts_browser_import_arguments():
    vscode = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert vscode.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert vscode._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    assert import_library()._playwright is None


def test_reports_the_version_of_its_package():
    assert import_library().ROBOT_LIBRARY_VERSION == version("robotframework-vscode")


@pytest.mark.parametrize(
    "method",
    [
        VSCode.VSCode.start_vs_code,
        VSCode.VSCode.close_vs_code,
        VSCode.VSCode.get_vs_code_instance_directories,
        VSCode.VSCode.execute_vs_code_cli_command,
        VSCode.VSCode.evaluate_in_extension_host,
    ],
)
def test_documents_every_argument_of_its_keywords(method):
    arguments = list(inspect.signature(method).parameters)[1:]

    assert [name for name in arguments if f"``{name}``" not in (method.__doc__ or "")] == []


@pytest.fixture
def open_instance(monkeypatch, tmp_path):
    """The library with an open instance, and the calls of the evaluation in its extension host."""
    vscode = import_library("timeout=5s")
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")
    vscode._instances()["browser=open"] = Instance(tmp_path / "code", directories)
    calls: list[tuple[Any, ...]] = []

    def run_in_extension_host(*args):
        calls.append(args)
        return "result"

    monkeypatch.setattr(VSCode, "run_in_extension_host", run_in_extension_host)
    return vscode, calls


def test_evaluates_in_the_extension_host_of_the_active_instance(open_instance, tmp_path):
    vscode, calls = open_instance

    result = vscode.evaluate_in_extension_host("(vscode, arg) => {", "return arg;", "}", arg=42, workspace=tmp_path)

    assert result == "result"
    user_data, script, arg, workspace, page_workspace_id, timeout = calls[0]
    assert (user_data, script, arg, workspace, timeout) == (
        tmp_path / "user-data",
        "(vscode, arg) => {\nreturn arg;\n}",
        42,
        tmp_path,
        5.0,
    )
    assert page_workspace_id == vscode._page_workspace_id


def test_evaluating_in_the_extension_host_of_another_application_fails(open_instance, monkeypatch):
    vscode, calls = open_instance
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=app"])

    with pytest.raises(
        AssertionError, match=r"^'browser=app' is not an open VS Code instance started by 'Start VS Code'"
    ):
        vscode.evaluate_in_extension_host("() => 1")
    assert calls == []


def test_evaluating_in_the_extension_host_without_an_open_instance_fails(open_instance, monkeypatch):
    vscode, calls = open_instance
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: [])

    with pytest.raises(AssertionError, match=r"^No VS Code instance is open\.$"):
        vscode.evaluate_in_extension_host("() => 1")
    assert calls == []


@pytest.mark.parametrize(("found", "workspace_id"), [({"workspaceId": "id-a"}, "id-a"), ({"workspaceId": None}, None)])
def test_reads_the_workspace_of_the_active_pages_window(monkeypatch, found, workspace_id):
    vscode = import_library()
    evaluated: list[tuple[Any, ...]] = []

    def evaluate_javascript(*args):
        evaluated.append(args)
        return found

    monkeypatch.setattr(vscode, "evaluate_javascript", evaluate_javascript)

    assert vscode._page_workspace_id() == workspace_id
    assert evaluated == [(None, PAGE_WORKSPACE_ID)]


def test_cannot_read_the_workspace_of_a_page_that_is_no_workbench_window(monkeypatch):
    vscode = import_library()
    monkeypatch.setattr(vscode, "evaluate_javascript", lambda *args: None)

    with pytest.raises(UnknownWorkspaceError):
        vscode._page_workspace_id()


def test_reads_the_page_again_when_it_cannot_be_read_for_the_moment(monkeypatch):
    vscode = import_library()

    def evaluate_javascript(*args):
        # Browser reports Playwright's errors as AssertionError.
        raise AssertionError("Error: page.evaluate: Execution context was destroyed")

    monkeypatch.setattr(vscode, "evaluate_javascript", evaluate_javascript)

    with pytest.raises(PageNotReadyError, match="Execution context was destroyed"):
        vscode._page_workspace_id()


def test_other_errors_while_reading_the_page_fail_at_once(monkeypatch):
    vscode = import_library()

    def evaluate_javascript(*args):
        raise ConnectionError("Playwright process has been terminated with code 1")

    monkeypatch.setattr(vscode, "evaluate_javascript", evaluate_javascript)

    with pytest.raises(ConnectionError, match="Playwright process has been terminated"):
        vscode._page_workspace_id()


@pytest.fixture
def recorded_cli(monkeypatch, tmp_path):
    """The library with a fake command-line script that records its calls."""
    vscode = import_library()
    vscode.outputdir = str(tmp_path / "output")
    calls: list[dict[str, Any]] = []

    def run_cli(cli, directories, args, env):
        calls.append({"cli": cli, "directories": directories, "args": args, "env": env})
        return "listed\n"

    monkeypatch.setattr(VSCode, "run_cli", run_cli)
    monkeypatch.setattr(VSCode, "cli_path", lambda executable: executable.parent / "bin" / "code")
    return vscode, calls


def test_cli_runs_on_the_active_instance(recorded_cli, monkeypatch, tmp_path):
    vscode, calls = recorded_cli
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")
    vscode._instances()["browser=open"] = Instance(tmp_path / "code", directories)

    output = vscode.execute_vs_code_cli_command("--list-extensions")

    [call] = calls
    assert output == "listed\n"
    assert call["cli"] == tmp_path / "bin" / "code"
    assert call["directories"] == directories
    assert call["args"] == ("--list-extensions",)


def test_cli_runs_on_the_environment_of_a_given_executable(recorded_cli, monkeypatch, tmp_path):
    vscode, calls = recorded_cli
    monkeypatch.setattr(VSCode, "installed_executable", lambda executable: tmp_path / "installed" / "code")
    prepared = tmp_path / "prepared-extensions"

    vscode.execute_vs_code_cli_command(
        "--install-extension", "ms-python.python", executable=Path("code"), extensions_dir=prepared
    )

    [call] = calls
    assert call["cli"] == tmp_path / "installed" / "bin" / "code"
    assert call["directories"].extensions == prepared
    assert call["directories"].user_data == tmp_path / "output" / "vscode" / "1" / "user-data"


def test_cli_runs_without_vs_code_variables_and_starts_no_process(recorded_cli, monkeypatch, tmp_path):
    vscode, calls = recorded_cli
    monkeypatch.setattr(VSCode, "installed_executable", lambda executable: tmp_path / "code")
    monkeypatch.setenv("VSCODE_IPC_HOOK_CLI", "/tmp/vscode-ipc.sock")
    monkeypatch.setenv("ELECTRON_RUN_AS_NODE", "1")
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.setenv("XDG_SESSION_TYPE", "wayland")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)
    monkeypatch.setattr(playwright, "run", fail)

    vscode.execute_vs_code_cli_command("--list-extensions", executable=Path("code"))

    [call] = calls
    assert "VSCODE_IPC_HOOK_CLI" not in call["env"]
    assert "ELECTRON_RUN_AS_NODE" not in call["env"]
    # Without a display, a call that VS Code's script does not take as a command opens no window.
    display = ("DISPLAY", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE")
    assert [name in call["env"] for name in display] == [sys.platform != "linux"] * len(display)


@pytest.mark.parametrize(
    ("args", "options", "message"),
    [
        ((), {"executable": Path("code")}, r"^Execute VS Code CLI Command needs the script's arguments"),
        (("--install-extension", ""), {"executable": Path("code")}, r"^Argument 2 of the script is empty\."),
        (("--list-extensions",), {"extensions_dir": Path("ext")}, r"^'user_data_dir' and 'extensions_dir' need"),
        (
            ("--list-extensions", "--extensions-dir", "ext"),
            {"executable": Path("code")},
            r"cannot get '--extensions-dir'",
        ),
        (("--user-data-dir=data", "--list-extensions"), {}, r"^The script cannot get '--user-data-dir=data'"),
    ],
)
def test_cli_refuses_calls_before_the_script_runs(recorded_cli, tmp_path, args, options, message):
    vscode, calls = recorded_cli

    with pytest.raises(ValueError, match=message):
        vscode.execute_vs_code_cli_command(*args, **options)
    assert calls == []
    assert not (tmp_path / "output").exists()


def test_cli_without_a_command_line_script_creates_no_directories(recorded_cli, monkeypatch, tmp_path):
    vscode, calls = recorded_cli
    monkeypatch.setattr(VSCode, "installed_executable", lambda executable: tmp_path / "code")

    def no_script(executable):
        raise ValueError("No VS Code command-line script found.")

    monkeypatch.setattr(VSCode, "cli_path", no_script)

    with pytest.raises(ValueError, match="No VS Code command-line script found"):
        vscode.execute_vs_code_cli_command("--list-extensions", executable=Path("code"), extensions_dir=Path("ext"))
    assert calls == []
    assert not (tmp_path / "output").exists()
    assert not (tmp_path / "ext").exists()


def test_cli_without_an_open_instance_names_executable(recorded_cli, monkeypatch):
    vscode, calls = recorded_cli

    def ask_browser(browser):
        raise AssertionError("Asking Browser for the active instance starts its Playwright process.")

    monkeypatch.setattr(vscode, "get_browser_ids", ask_browser)

    with pytest.raises(ValueError, match=r"^No VS Code instance is open\. Give 'executable'"):
        vscode.execute_vs_code_cli_command("--list-extensions")
    assert calls == []
