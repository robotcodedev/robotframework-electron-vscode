from datetime import timedelta
from typing import Any

import pytest
from Browser.utils.data_types import AutoClosingLevel, ColorScheme
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import HIDDEN_KEYWORDS, Electron
from VSCode import Instance
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

    assert added == {"Open VS Code", "Close VS Code", "Get VS Code Instance Directories"}


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


def test_passes_the_launch_options_on(monkeypatch, tmp_path):
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


def test_converts_browser_import_arguments():
    vscode = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert vscode.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert vscode._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    assert import_library()._playwright is None
