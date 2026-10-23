import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from assertionengine import AssertionOperator
from Browser import Browser
from Browser.utils.data_types import (
    AutoClosingLevel,
    ColorScheme,
    SelectionType,
    ShowActions,
    ShowActionsPosition,
    SizeFields,
)
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


@pytest.fixture
def fake_windows(monkeypatch):
    """Fakes electron.js's window functions for an active application with two windows, and records the calls."""
    electron = import_library()
    calls: list[tuple[str, dict[str, Any]]] = []
    results: dict[str, Any] = {
        "robotframeworkElectronWindows": [{"id": 1, "title": "First"}, {"id": 2, "title": "Second"}],
        "robotframeworkElectronAdjustWindow": None,
        "robotframeworkElectronGetWindow": {"state": "normal", "width": 800, "height": 600},
    }

    def call_js_keyword(name, **arguments):
        calls.append((name, arguments))
        result = results[name]
        return result() if callable(result) else result

    monkeypatch.setattr(electron, "get_browser_ids", lambda selection: ["browser=app"])
    monkeypatch.setattr(electron, "init_js_extension", lambda path: None)
    monkeypatch.setattr(electron, "call_js_keyword", call_js_keyword)
    return electron, calls, results


def test_returns_the_window_ids(fake_windows):
    electron, calls, _ = fake_windows

    assert electron.get_window_ids() == ["window=1", "window=2"]
    assert calls == [("robotframeworkElectronWindows", {"browserId": "browser=app", "active": False})]


def test_returns_the_id_of_the_window_of_the_active_page(fake_windows):
    electron, calls, results = fake_windows
    results["robotframeworkElectronWindows"] = [{"id": 2, "title": "Second"}]

    assert electron.get_window_ids(SelectionType.ACTIVE) == ["window=2"]
    assert calls[0][1]["active"] is True


def test_returns_the_window_titles(fake_windows):
    electron, _, _ = fake_windows

    assert electron.get_window_titles() == ["First", "Second"]


@pytest.mark.parametrize(
    ("keyword", "state"),
    [("maximize_window", "maximized"), ("minimize_window", "minimized"), ("restore_window", "normal")],
)
def test_changes_the_state_of_a_window(fake_windows, keyword, state):
    electron, calls, _ = fake_windows

    getattr(electron, keyword)("title=Settings")

    arguments = {"browserId": "browser=app", "window": "title=Settings", "state": state, "size": None}
    assert calls == [("robotframeworkElectronAdjustWindow", arguments)]


def test_sizes_the_window_of_the_active_page_in_its_normal_state(fake_windows):
    electron, calls, _ = fake_windows

    electron.set_window_size(1024, 700)

    arguments = {"browserId": "browser=app", "window": None, "state": "normal", "size": {"width": 1024, "height": 700}}
    assert calls == [("robotframeworkElectronAdjustWindow", arguments)]


def test_returns_the_content_size_of_a_window(fake_windows):
    electron, calls, _ = fake_windows

    assert electron.get_window_size() == {"width": 800, "height": 600}
    assert electron.get_window_size(SizeFields.width, window="window=2") == 800
    assert calls[1] == ("robotframeworkElectronGetWindow", {"browserId": "browser=app", "window": "window=2"})


def test_returns_the_state_of_a_window(fake_windows):
    electron, _, _ = fake_windows

    assert electron.get_window_state(AssertionOperator["=="], "normal") == "normal"


def test_window_getters_assert_as_browsers_getters_do(fake_windows):
    electron, _, _ = fake_windows

    with pytest.raises(AssertionError, match="Window state 'normal'"):
        electron.get_window_state(AssertionOperator["=="], "maximized")


@pytest.mark.parametrize(
    "keyword",
    ["get_window_ids", "get_window_titles", "maximize_window", "minimize_window", "restore_window", "get_window_state"],
)
def test_window_keywords_need_an_application(fake_windows, monkeypatch, keyword):
    electron, calls, _ = fake_windows
    monkeypatch.setattr(electron, "get_browser_ids", lambda selection: [])

    with pytest.raises(AssertionError, match=r"No application is open\."):
        getattr(electron, keyword)()
    assert calls == []


def browser_catalog(*titles: str) -> list[dict[str, Any]]:
    """Browser's catalog with the active application ``browser=app``, which has a page with each title."""
    pages = [
        {"id": f"page={number}", "title": title, "url": "file:///page.html", "type": "page"}
        for number, title in enumerate(titles, 1)
    ]
    context = {"id": "context=app", "activePage": "page=1", "pages": pages}
    return [{"id": "browser=app", "type": "electron", "activeBrowser": True, "contexts": [context]}]


@pytest.fixture
def fake_switching(fake_windows, monkeypatch):
    """Adds Browser's catalog, which takes the next of ``catalogs`` on each read, and records the page switches.

    electron.js finds the second window, whose page has the title ``Second``, and the active page is that window's.
    A switch to ``page=other`` makes ``browser=other`` the active application, as Browser does.
    """
    electron, calls, results = fake_windows
    catalogs = [browser_catalog("First", "Second")]
    switches: list[str] = []
    active = ["browser=app"]

    def switch_page(page_id):
        switches.append(page_id)
        active[0] = "browser=other" if page_id == "page=other" else "browser=app"
        return "page=1"

    def get_browser_catalog(*args):
        return catalogs.pop(0) if len(catalogs) > 1 else catalogs[0]

    monkeypatch.setattr(electron, "get_browser_ids", lambda selection: list(active))
    monkeypatch.setattr(electron, "get_browser_catalog", get_browser_catalog)
    monkeypatch.setattr(electron, "switch_page", switch_page)
    results["robotframeworkElectronWindowPage"] = {"id": 2, "pageTitle": "Second"}
    results["robotframeworkElectronWindowOfPage"] = 2
    return electron, calls, results, catalogs, switches


def test_finds_the_page_of_a_window_in_the_catalog(fake_switching):
    electron, _, _, _, _ = fake_switching

    assert electron._page_of_window(2, "Second", time.monotonic()) == "page=2"


def test_waits_for_the_page_of_a_window(fake_switching):
    electron, calls, _, catalogs, _ = fake_switching
    # Browser has not indexed the page yet, and then it could not read its title in time.
    catalogs[:] = [browser_catalog("First"), browser_catalog("First", ""), browser_catalog("First", "Second")]

    assert electron._page_of_window(2, "Second", time.monotonic() + 5) == "page=2"
    # Meanwhile, it reads the title again, without waiting, because the page can change it.
    arguments = {"browserId": "browser=app", "window": "window=2", "defaultTimeout": 0}
    assert calls[0] == ("robotframeworkElectronWindowPage", arguments)


def test_reads_the_title_again_while_the_page_has_none(fake_switching):
    electron, _, _, _, _ = fake_switching

    assert electron._page_of_window(2, None, time.monotonic() + 5) == "page=2"


@pytest.mark.parametrize(
    ("page_title", "titles", "error"),
    [
        (None, ("First", "Second"), r"The page of the window 'window=2' has no title"),
        ("Second", ("First",), r"No page of the application has the title 'Second' of the window 'window=2'\."),
        ("Second", ("Second", "Second"), r"The pages page=1, page=2 all have the title 'Second'"),
    ],
)
def test_page_search_fails_without_exactly_one_page(fake_switching, page_title, titles, error):
    electron, _, _, catalogs, _ = fake_switching
    catalogs[:] = [browser_catalog(*titles)]

    with pytest.raises(AssertionError, match=error):
        electron._page_of_window(2, page_title, time.monotonic())


def test_switches_to_a_window_by_its_title(fake_switching):
    electron, calls, _, _, switches = fake_switching

    assert electron.switch_window("title=Second") == "page=1"
    assert switches == ["page=2"]
    assert calls[0] == ("robotframeworkElectronWindowPage", {"browserId": "browser=app", "window": "title=Second"})


def test_switches_back_when_the_page_is_not_the_windows_own(fake_switching):
    electron, _, results, _, switches = fake_switching
    results["robotframeworkElectronWindowOfPage"] = 1

    with pytest.raises(AssertionError, match=r"The page 'page=2' is not the own page of the window 'window=2'\."):
        electron.switch_window("window=2")
    assert switches == ["page=2", "page=1"]


@pytest.mark.parametrize(("page_id", "switched"), [("page=2", "page=2"), ("NEW", "NEW"), ("new", "NEW")])
def test_switches_to_a_page_that_is_a_window(fake_switching, page_id, switched):
    electron, calls, _, _, switches = fake_switching

    assert electron.switch_window(page_id) == "page=1"
    assert switches == [switched]
    assert [name for name, _ in calls] == ["robotframeworkElectronWindowOfPage"]


def test_checks_a_page_in_the_application_that_it_belongs_to(fake_switching):
    electron, calls, _, _, switches = fake_switching

    assert electron.switch_window("page=other") == "page=1"
    assert switches == ["page=other"]
    assert calls == [("robotframeworkElectronWindowOfPage", {"browserId": "browser=other"})]


@pytest.mark.parametrize(
    ("page_id", "error"),
    [("page=3", r"The page 'page=3' is not a window"), ("NEW", r"The newest page is not a window")],
)
def test_switches_back_from_a_page_that_is_no_window(fake_switching, page_id, error):
    electron, _, results, _, switches = fake_switching
    results["robotframeworkElectronWindowOfPage"] = None

    with pytest.raises(AssertionError, match=error):
        electron.switch_window(page_id)
    assert switches == [page_id, "page=1"]


def test_switching_windows_needs_an_application(fake_switching, monkeypatch):
    electron, calls, _, _, switches = fake_switching
    monkeypatch.setattr(electron, "get_browser_ids", lambda selection: [])

    with pytest.raises(AssertionError, match=r"No application is open\."):
        electron.switch_window("title=Second")
    assert (calls, switches) == ([], [])


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
