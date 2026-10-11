from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from Browser import Browser
from Browser.utils.data_types import AutoClosingLevel
from robot.running.arguments.typeinfo import TypeInfo
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import Electron, RecordVideo, ShowActions, __version__


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


def import_library(*args: str) -> Electron:
    electron: Electron = RobotLibrary.from_name("Electron", args=list(args)).instance
    return electron


def test_contains_every_browser_keyword():
    electron = import_library()

    assert set(Browser().get_keyword_names()) <= set(electron.get_keyword_names())


def test_converts_browser_import_arguments():
    electron = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert electron.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert electron._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    electron = import_library()

    assert electron._playwright is None


def test_reports_own_version():
    assert import_library().ROBOT_LIBRARY_VERSION == __version__


def test_record_video_converts_robot_framework_values():
    value = "{'size': {'width': '1920', 'height': '1080'}, 'showActions': {'duration': '800', 'cursor': 'none'}}"

    converted = TypeInfo.from_type_hint(RecordVideo).convert(value)

    assert converted == {"size": {"width": 1920, "height": 1080}, "showActions": {"duration": 800, "cursor": "none"}}


def test_record_video_rejects_unknown_keys():
    with pytest.raises(ValueError, match="'speed' not allowed"):
        TypeInfo.from_type_hint(RecordVideo).convert("{'speed': 2}")


@pytest.fixture
def fake_launch(tmp_path, monkeypatch):
    """Replaces the start in Browser's Node process and records its arguments."""
    executable = tmp_path / "bin" / "electron"
    executable.parent.mkdir()
    executable.write_text("")
    executable.chmod(0o755)
    monkeypatch.delenv("ROBOT_FRAMEWORK_BROWSER_TRACING", raising=False)
    electron = import_library()
    calls: list[dict[str, Any]] = []

    def call_js_keyword(name, **arguments):
        calls.append(arguments)
        return {"browserId": "browser", "contextId": "context"}

    monkeypatch.setattr(electron, "init_js_extension", lambda path: None)
    monkeypatch.setattr(electron, "call_js_keyword", call_js_keyword)
    return electron, calls


def test_relative_paths_are_relative_to_the_working_directory(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.new_electron_application(Path("bin/electron"), cwd=Path("work"))

    assert calls[0]["executablePath"] == str(tmp_path / "bin" / "electron")
    assert calls[0]["cwd"] == str(tmp_path / "work")


def test_gives_the_application_the_library_timeout(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.new_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["defaultTimeout"] == int(electron.timeout)


def test_application_runs_in_the_working_directory_by_default(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.new_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["cwd"] == str(tmp_path)


def test_first_window_closed_during_the_start(fake_launch, tmp_path):
    electron, _ = fake_launch

    browser_id, context_id, page = electron.new_electron_application(tmp_path / "bin" / "electron")

    assert (browser_id, context_id, page["page_id"]) == ("browser", "context", "")


def test_no_recording_by_default(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.new_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["recordVideo"] is None
    assert calls[0]["tracing"] is None


def test_recording_options_come_from_browser(fake_launch, tmp_path):
    electron, calls = fake_launch
    electron.outputdir = str(tmp_path)
    show_actions: ShowActions = {"duration": 800, "position": "top-right"}

    electron.new_electron_application(
        tmp_path / "bin" / "electron", record_video={"showActions": show_actions}, tracing=True
    )

    assert calls[0]["recordVideo"] == {
        "dir": str((tmp_path / "browser" / "video").resolve()),
        "size": {"width": 1280, "height": 720},
        "showActions": show_actions,
    }
    assert calls[0]["tracing"] == str(tmp_path / "browser" / "traces")
    assert electron.tracing_contexts == ["context"]


def test_har_options_come_from_browser(fake_launch, tmp_path):
    electron, calls = fake_launch
    electron.outputdir = str(tmp_path)

    electron.new_electron_application(tmp_path / "bin" / "electron", record_har={"path": "network.har"})

    assert calls[0]["recordHar"] == {"path": str((tmp_path / "network.har").resolve())}
