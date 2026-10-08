import json
import re

import pytest
from Browser import playwright
from robot.libdoc import LibraryDocumentation

from Electron import __version__


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def unresolved_links(library: str) -> set[str]:
    doc = LibraryDocumentation(library)
    doc.convert_docs_to_html()
    html = json.dumps(doc.to_dictionary())
    return set(re.findall(r'<span class=\\"name\\">([^<]+)</span>', html))


def test_reports_package_version():
    assert LibraryDocumentation("Electron").version == __version__


def test_has_no_unresolved_links_beyond_browser():
    assert unresolved_links("Electron") <= unresolved_links("Browser")


def test_libdoc_starts_no_process(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)
    monkeypatch.setattr(playwright, "run", fail)

    assert LibraryDocumentation("Electron").keywords


def test_helper_libdoc_documents_its_keyword_without_starting_a_process(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)

    doc = LibraryDocumentation("Electron.Helper")

    assert doc.version == __version__
    assert [kw.name for kw in doc.keywords] == ["Get Electron Executable"]
    assert doc.keywords[0].doc
    assert unresolved_links("Electron.Helper") == set()
