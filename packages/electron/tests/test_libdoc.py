import inspect
import json
import re
from pathlib import Path

import pytest
from Browser import playwright
from robot.libdoc import LibraryDocumentation

from Electron import Electron, __version__


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


def test_intro_is_the_librarys_own_followed_by_browsers_sections():
    doc = LibraryDocumentation("Electron").doc

    assert doc.startswith("Electron library is a Robot Framework library for testing Electron applications.")
    assert "Browser library is a browser automation library" not in doc
    assert "= Assertions =" in doc


def test_import_is_documented_with_browsers_arguments():
    init = LibraryDocumentation("Electron").inits[0]

    assert init.doc.startswith("Electron library takes the same import arguments as the Browser library.")
    assert init.args.docs["timeout"].startswith("Timeout for keywords that operate on elements.")
    assert [arg.name for arg in init.args] == [arg.name for arg in LibraryDocumentation("Browser").inits[0].args]


def own_keywords(library: str) -> list:
    package = Path(inspect.getfile(Electron)).parent
    return [kw for kw in LibraryDocumentation(library).keywords if Path(kw.source).is_relative_to(package)]


@pytest.mark.parametrize("library", ["Electron", "Electron.Helper"])
def test_own_keywords_document_every_argument_and_return_value(library):
    keywords = own_keywords(library)

    assert keywords
    for keyword in keywords:
        assert all(keyword.args.docs.get(arg.name) for arg in keyword.args if arg.name), keyword.name
        returns_nothing = keyword.args.return_type is None or keyword.args.return_type.type is type(None)
        assert returns_nothing or keyword.args.return_doc, keyword.name


@pytest.mark.parametrize(
    ("library", "name"), [("Electron", "New Electron Application"), ("Electron.Helper", "Get Electron Executable")]
)
def test_keywords_document_the_exceptions_for_invalid_input(library, name):
    keyword = next(kw for kw in own_keywords(library) if kw.name == name)

    assert "ValueError" in keyword.args.raises
