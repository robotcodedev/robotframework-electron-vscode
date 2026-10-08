import json
import re
from pathlib import Path

import pytest
from Browser import playwright
from robot.libdoc import LibraryDocumentation

from VSCode import VSCode, __version__, download
from VSCode.Helper import Helper


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def no_network(monkeypatch):
    def fail(url):
        raise AssertionError(f"network access to {url}")

    monkeypatch.setattr(download, "_open", fail)


def test_returns_given_executable_without_downloading(no_network, tmp_path):
    executable = Helper().get_vs_code_executable("stable", Path("/usr/share/code/code"), tmp_path)

    assert executable == str(Path("/usr/share/code/code"))
    assert list(tmp_path.iterdir()) == []


def test_libdoc_lists_only_the_helper_keyword_without_starting_a_process(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)
    monkeypatch.setattr(playwright, "run", fail)

    doc = LibraryDocumentation("VSCode.Helper")

    assert doc.version == __version__
    assert [keyword.name for keyword in doc.keywords] == ["Get VS Code Executable"]
    assert doc.keywords[0].doc


def test_helper_documentation_has_no_unresolved_links():
    doc = LibraryDocumentation("VSCode.Helper")
    doc.convert_docs_to_html()
    html = json.dumps(doc.to_dictionary())

    assert re.findall(r'<span class=\\"name\\">([^<]+)</span>', html) == []


def test_vscode_library_no_longer_downloads_on_its_own():
    assert "Download VS Code" not in VSCode().get_keyword_names()
