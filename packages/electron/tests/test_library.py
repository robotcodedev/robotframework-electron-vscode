from datetime import timedelta
from pathlib import Path

import pytest
from Browser import Browser
from Browser.utils.data_types import AutoClosingLevel
from robot.running.arguments.typeinfo import TypeInfo
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import Electron, RecordVideo, __version__


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


def import_library(*args: str) -> Electron:
    return RobotLibrary.from_name("Electron", args=list(args)).instance


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


def test_no_video_options_without_record_video():
    assert import_library()._video_options(None) is None


def test_video_defaults_to_browsers_folder_and_size(tmp_path):
    electron = import_library()
    electron.outputdir = str(tmp_path)

    options = electron._video_options({})

    assert options["dir"] == str(tmp_path / "browser" / "video")
    assert options["size"] == {"width": 1280, "height": 720}


def test_video_folder_size_and_action_overlay_are_passed_on(tmp_path):
    electron = import_library()
    electron.outputdir = str(tmp_path)
    show_actions = {"duration": 800, "position": "top-right"}

    options = electron._video_options(
        {"dir": "demo", "size": {"width": 1920, "height": 1080}, "showActions": show_actions}
    )

    assert Path(options["dir"]) == (tmp_path / "browser" / "video" / "demo").resolve()
    assert options["size"] == {"width": 1920, "height": 1080}
    assert options["showActions"] == show_actions


def test_record_video_converts_robot_framework_values():
    value = "{'size': {'width': '1920', 'height': '1080'}, 'showActions': {'duration': '800', 'cursor': 'none'}}"

    converted = TypeInfo.from_type_hint(RecordVideo).convert(value)

    assert converted == {"size": {"width": 1920, "height": 1080}, "showActions": {"duration": 800, "cursor": "none"}}


def test_record_video_rejects_unknown_keys():
    with pytest.raises(ValueError, match="'speed' not allowed"):
        TypeInfo.from_type_hint(RecordVideo).convert("{'speed': 2}")


def test_no_har_options_without_record_har():
    assert import_library()._har_options(None) is None


def test_har_path_is_relative_to_the_output_directory(tmp_path):
    electron = import_library()
    electron.outputdir = str(tmp_path)

    options = electron._har_options({"path": "network.har", "omitContent": True})

    assert options == {"path": str(tmp_path / "network.har"), "omitContent": True}


def test_absolute_har_path_is_kept(tmp_path):
    electron = import_library()
    electron.outputdir = str(tmp_path / "output")

    options = electron._har_options({"path": str(tmp_path / "network.har")})

    assert options == {"path": str(tmp_path / "network.har")}


def test_record_har_without_path_fails():
    with pytest.raises(ValueError, match="needs a 'path'"):
        import_library()._har_options({"omitContent": True})
