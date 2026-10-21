from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from Browser import Browser
from Browser.utils.data_types import AutoClosingLevel, ColorScheme, SelectionType, ShowActions, ShowActionsPosition
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import HIDDEN_KEYWORDS, Electron, __version__


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


def import_library(*args: str) -> Electron:
    electron: Electron = RobotLibrary.from_name("Electron", args=list(args)).instance
    return electron


def test_contains_every_browser_keyword_except_the_hidden_ones():
    names = set(import_library().get_keyword_names())

    assert set(Browser().get_keyword_names()) - HIDDEN_KEYWORDS <= names
    assert not names & HIDDEN_KEYWORDS


def test_hidden_keywords_are_browser_keywords():
    browser = Browser()

    assert {name for name in HIDDEN_KEYWORDS if name not in browser.keywords} == set()


def test_hides_translated_keyword_names():
    electron = import_library()
    electron.keywords["Uusi Konteksti"] = electron.keywords["new_context"]

    assert "Uusi Konteksti" not in electron.get_keyword_names()


def test_converts_browser_import_arguments():
    electron = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert electron.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert electron._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    electron = import_library()

    assert electron._playwright is None


def test_reports_own_version():
    assert import_library().ROBOT_LIBRARY_VERSION == __version__


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

    electron.start_electron_application(Path("bin/electron"), cwd=Path("work"))

    assert calls[0]["executablePath"] == str(tmp_path / "bin" / "electron")
    assert calls[0]["cwd"] == str(tmp_path / "work")


def test_application_runs_in_the_working_directory_by_default(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.start_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["cwd"] == str(tmp_path)


def test_first_window_closed_during_the_start(fake_launch, tmp_path):
    electron, _ = fake_launch

    application, page = electron.start_electron_application(tmp_path / "bin" / "electron")

    assert (application, page["page_id"]) == ("browser", "")


def test_no_recording_by_default(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.start_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["recordVideo"] is None
    assert calls[0]["tracing"] is None


def test_recording_options_come_from_browser(fake_launch, tmp_path):
    electron, calls = fake_launch
    electron.outputdir = str(tmp_path)
    show_actions: ShowActions = {"duration": 800, "position": ShowActionsPosition.top_right}

    electron.start_electron_application(
        tmp_path / "bin" / "electron", record_video={"fps": 10, "showActions": show_actions}, tracing=True
    )

    assert calls[0]["recordVideo"] == {
        "dir": str((tmp_path / "browser" / "video").resolve()),
        "size": {"width": 1280, "height": 720},
        "fps": 10,
        "showActions": show_actions,
    }
    assert calls[0]["tracing"] == str(tmp_path / "browser" / "traces")


def test_har_options_come_from_browser(fake_launch, tmp_path):
    electron, calls = fake_launch
    electron.outputdir = str(tmp_path)

    electron.start_electron_application(tmp_path / "bin" / "electron", record_har={"path": "network.har"})

    assert calls[0]["recordHar"] == {"path": str((tmp_path / "network.har").resolve())}


def test_temporary_trace_files_go_to_browsers_folder(fake_launch, tmp_path):
    electron, calls = fake_launch
    electron.outputdir = str(tmp_path)

    electron.start_electron_application(tmp_path / "bin" / "electron")

    assert Path(calls[0]["tracesDir"]).parent == tmp_path / "browser" / "traces" / "temp"


def test_no_launch_options_by_default(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.start_electron_application(tmp_path / "bin" / "electron")

    assert calls[0]["launchOptions"] == {}


def test_launch_options_have_playwrights_names(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.start_electron_application(
        tmp_path / "bin" / "electron",
        color_scheme=ColorScheme.dark,
        locale="de-DE",
        timezone_id="Asia/Tokyo",
        bypass_csp=True,
    )

    assert calls[0]["launchOptions"] == {
        "colorScheme": "dark",
        "locale": "de-DE",
        "timezoneId": "Asia/Tokyo",
        "bypassCSP": True,
    }


def test_null_color_scheme_leaves_it_to_the_application(fake_launch, tmp_path):
    electron, calls = fake_launch

    electron.start_electron_application(tmp_path / "bin" / "electron", color_scheme=ColorScheme["null"])

    assert calls[0]["launchOptions"] == {}


def test_evaluates_in_the_main_process_of_the_active_application(fake_launch, monkeypatch):
    electron, calls = fake_launch
    monkeypatch.setattr(electron, "get_browser_ids", lambda browser: ["browser=app"])

    electron.evaluate_in_main_process("({ app }) =>", "app.getName()")

    assert calls[0] == {"browserId": "browser=app", "script": "({ app }) =>\napp.getName()", "arg": None}


def test_evaluating_without_an_open_application_fails(fake_launch, monkeypatch):
    electron, calls = fake_launch
    monkeypatch.setattr(electron, "get_browser_ids", lambda browser: [])

    with pytest.raises(AssertionError, match=r"No application is open\."):
        electron.evaluate_in_main_process("() => 1")
    assert calls == []


def test_evaluates_in_the_main_process_of_a_given_application(fake_launch):
    electron, calls = fake_launch

    electron.evaluate_in_main_process("(electron, arg) => arg", arg={"answer": 42}, application="browser=other")

    assert calls[0] == {"browserId": "browser=other", "script": "(electron, arg) => arg", "arg": {"answer": 42}}


def test_returns_the_page_and_the_video_that_browser_reports(fake_launch, monkeypatch, tmp_path):
    electron, _ = fake_launch
    adopted = {"browserId": "browser", "contextId": "context", "pageId": "page=window", "videoPath": "window.webm"}
    monkeypatch.setattr(electron, "call_js_keyword", lambda name, **arguments: adopted)

    application, page = electron.start_electron_application(tmp_path / "bin" / "electron")

    assert (application, page["page_id"], page["video_path"]) == ("browser", "page=window", "window.webm")


@pytest.fixture
def two_applications(monkeypatch):
    """Fakes Browser's state with two applications, the second one active, and records switches."""
    electron = import_library()
    switches: list[str] = []
    catalog = [
        {
            "id": "browser=first",
            "type": "electron",
            "activeBrowser": False,
            "contexts": [
                {
                    "id": "context=first",
                    "activePage": "page=window",
                    "pages": [
                        {"id": "page=window", "title": "Window", "url": "file:///window.html", "type": "page"},
                        {"id": "page=view", "title": "View", "url": "file:///view.html", "type": "page"},
                    ],
                }
            ],
        },
        {"id": "browser=second", "type": "electron", "activeBrowser": True, "contexts": []},
    ]

    def switch_browser(application):
        switches.append(application)
        return "browser=second"

    def get_browser_ids(selection):
        return ["browser=second"] if selection.name in ("ACTIVE", "CURRENT") else ["browser=first", "browser=second"]

    monkeypatch.setattr(electron, "switch_browser", switch_browser)
    monkeypatch.setattr(electron, "get_browser_ids", get_browser_ids)
    monkeypatch.setattr(electron, "get_browser_catalog", lambda *args: catalog)
    return electron, switches


def test_switches_to_another_application(two_applications):
    electron, switches = two_applications

    previous = electron.switch_electron_application("browser=first")

    assert (previous, switches) == ("browser=second", ["browser=first"])


def test_returns_the_ids_of_the_applications(two_applications):
    electron, _ = two_applications

    assert electron.get_electron_application_ids() == ["browser=first", "browser=second"]
    assert electron.get_electron_application_ids(SelectionType.ACTIVE) == ["browser=second"]


def test_returns_the_applications_with_their_pages(two_applications):
    electron, _ = two_applications

    assert electron.get_electron_application_catalog() == [
        {
            "id": "browser=first",
            "active": False,
            "pages": [
                {"id": "page=window", "title": "Window", "url": "file:///window.html", "active": True},
                {"id": "page=view", "title": "View", "url": "file:///view.html", "active": False},
            ],
        },
        {"id": "browser=second", "active": True, "pages": []},
    ]
