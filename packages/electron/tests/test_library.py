from datetime import timedelta

import pytest
from Browser import Browser
from Browser.utils.data_types import AutoClosingLevel
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import Electron, __version__


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
