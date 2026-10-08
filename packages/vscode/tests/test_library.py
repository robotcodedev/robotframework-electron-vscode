import json
import re
from datetime import timedelta

import pytest
from Browser import playwright
from Browser.utils.data_types import AutoClosingLevel
from Electron import Electron
from robot.libdoc import LibraryDocumentation
from robot.running.testlibraries import TestLibrary as RobotLibrary

from VSCode import __version__


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


def import_library(*args: str):
    return RobotLibrary.from_name("VSCode", args=list(args)).instance


def unresolved_links(library: str) -> set[str]:
    doc = LibraryDocumentation(library)
    doc.convert_docs_to_html()
    html = json.dumps(doc.to_dictionary())
    return set(re.findall(r'<span class=\\"name\\">([^<]+)</span>', html))


def test_contains_every_electron_and_browser_keyword():
    vscode = import_library()

    assert set(Electron().get_keyword_names()) <= set(vscode.get_keyword_names())


def test_adds_only_open_and_close_vs_code_to_electron():
    added = set(import_library().get_keyword_names()) - set(Electron().get_keyword_names())

    assert added == {"Open VS Code", "Close VS Code"}


def test_converts_browser_import_arguments():
    vscode = import_library("timeout=5s", "auto_closing_level=SUITE")

    assert vscode.timeout == timedelta(seconds=5).total_seconds() * 1000
    assert vscode._auto_closing_level is AutoClosingLevel.SUITE


def test_import_starts_no_node_process():
    assert import_library()._playwright is None


def test_libdoc_reports_own_version_without_starting_a_process(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)
    monkeypatch.setattr(playwright, "run", fail)

    assert LibraryDocumentation("VSCode").version == __version__


def test_has_no_unresolved_links_beyond_browser():
    assert unresolved_links("VSCode") <= unresolved_links("Browser")
