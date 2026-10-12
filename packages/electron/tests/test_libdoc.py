import inspect
import json
import re
from pathlib import Path
from typing import Any

import pytest
from Browser import playwright
from robot.libdoc import LibraryDocumentation

from Electron import HIDDEN_KEYWORDS, Electron, __version__
from Electron._docs import KEYWORD_NOTES


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


def test_has_no_unresolved_links_beyond_browser_and_hidden_keywords():
    # Browser's keyword documentation links to keywords that the library hides; Libdoc shows them as names.
    hidden = {name.replace("_", " ") for name in HIDDEN_KEYWORDS}
    unresolved = {link.lower() for link in unresolved_links("Electron") - unresolved_links("Browser")}

    assert unresolved <= hidden


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


BROWSER_DOCUMENTATION = "https://marketsquare.github.io/robotframework-browser/Browser.html"


def test_intro_is_the_librarys_own_and_points_to_browsers_documentation():
    doc = LibraryDocumentation("Electron").doc

    assert doc.startswith("Electron library is a Robot Framework library for testing Electron applications.")
    assert "Browser library is a browser automation library" not in doc
    assert "Keywords that act on an element take a ``selector`` argument." not in doc
    assert "= Assertions =" in doc
    assert f"{BROWSER_DOCUMENTATION}#Assertions" in doc


def test_intro_compares_the_library_with_browser():
    doc = LibraryDocumentation("Electron").doc

    assert "== Compared with the Browser library ==" in doc
    assert "| ``Switch Browser`` | `Switch Electron Application` |" in doc
    assert all(f"``{name.replace('_', ' ').title()}``" in doc for name in HIDDEN_KEYWORDS)


def test_import_documentation_points_to_browsers_arguments():
    init = LibraryDocumentation("Electron").inits[0]
    text = " ".join(init.doc.split())

    assert text.startswith("Electron library takes the same import arguments as the Browser library")
    assert f"{BROWSER_DOCUMENTATION}#Importing" in init.doc
    assert [arg.name for arg in init.args] == [arg.name for arg in LibraryDocumentation("Browser").inits[0].args]


def own_keywords(library: str) -> list[Any]:
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


def note_html(library: str) -> dict[str, str]:
    """The HTML of the note on applications, by keyword name, for the keywords that have one."""
    doc = LibraryDocumentation(library)
    doc.convert_docs_to_html()
    marker = "<b>In Electron applications:</b>"
    return {kw.name: kw.doc[kw.doc.index(marker) :] for kw in doc.keywords if marker in kw.doc}


def test_browser_keywords_that_behave_differently_have_a_note():
    names = {name.replace("_", " ").title() for name in KEYWORD_NOTES}

    assert set(note_html("Electron")) == names


def test_notes_link_to_keywords_and_sections_of_the_library():
    notes = note_html("Electron")

    assert [name for name, html in notes.items() if '<span class="name">' in html] == []
    assert re.findall(r'<a href="#([^"]+)"[^>]*class="name">', notes["Close Page"]) == [
        "Evaluate%20JavaScript",
        "Browser%2C%20Context%20and%20Page",
    ]


def test_other_browser_keywords_keep_browsers_documentation():
    electron = {kw.name: kw.doc for kw in LibraryDocumentation("Electron").keywords}
    browser = {kw.name: kw.doc for kw in LibraryDocumentation("Browser").keywords}

    assert electron["Click"] == browser["Click"]
    assert electron["Close Page"].startswith(browser["Close Page"])


def test_evaluate_in_main_process_requires_a_function():
    keyword = next(kw for kw in LibraryDocumentation("Electron").keywords if kw.name == "Evaluate In Main Process")

    assert keyword.args.minargs == 1
    assert [arg.name for arg in keyword.args][:2] == ["function", "lines"]
