from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from Browser.utils.data_types import AutoClosingLevel, ColorScheme
from robot.running.testlibraries import TestLibrary as RobotLibrary

import VSCode
from Electron import HIDDEN_KEYWORDS, Electron
from VSCode import Instance
from VSCode.extension_host import PAGE_WORKSPACE_ID, PageNotReadyError, UnknownWorkspaceError
from VSCode.instance import InstanceDirectories


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
        "Open VS Code",
        "Close VS Code",
        "Get VS Code Instance Directories",
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


def test_instance_directories_of_a_browser_not_opened_by_open_vs_code_fail():
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

    monkeypatch.setattr(vscode, "new_electron_application", lambda *args, **kwargs: ("browser", {}))
    monkeypatch.setattr(vscode, "wait_for_elements_state", not_ready)
    monkeypatch.setattr(vscode, "close_browser", close_fails)

    with pytest.raises(TimeoutError, match="workbench not ready"):
        vscode.open_vs_code(executable=executable)
    assert vscode._instances() == {}


def recording_start(monkeypatch, tmp_path) -> tuple[Any, Path, dict[str, Any]]:
    """Imports the library with a fake start that records the arguments of `New Electron Application`."""
    executable = tmp_path / "code"
    executable.write_text("")
    executable.chmod(0o755)
    vscode = import_library()
    vscode.outputdir = str(tmp_path / "output")
    started: dict[str, Any] = {}

    def new_electron_application(*args, **kwargs):
        started.update(kwargs)
        return ("browser", {})

    monkeypatch.setattr(vscode, "new_electron_application", new_electron_application)
    monkeypatch.setattr(vscode, "wait_for_elements_state", lambda *args, **kwargs: None)
    return vscode, executable, started


def test_passes_the_launch_options_on(monkeypatch, tmp_path):
    vscode, executable, started = recording_start(monkeypatch, tmp_path)

    vscode.open_vs_code(
        executable=executable,
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

    vscode.open_vs_code(executable=executable)
    without = development_paths(started["args"])
    vscode.open_vs_code(executable=executable, extension_development_path=tmp_path / "extension")

    assert without == []
    assert development_paths(started["args"]) == [str(tmp_path / "extension")]


def test_converts_browser_import_arguments():
    vscode = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert vscode.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert vscode._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    assert import_library()._playwright is None


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
        AssertionError, match=r"^'browser=app' is not an open VS Code instance started by 'Open VS Code'"
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
