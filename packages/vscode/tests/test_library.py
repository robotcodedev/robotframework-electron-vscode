import inspect
import json
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from Browser import playwright
from Browser.utils.data_types import AutoClosingLevel
from robot.libdoc import LibraryDocumentation
from robot.running.testlibraries import TestLibrary as RobotLibrary

from Electron import Electron
from VSCode import Instance, VSCode, __version__
from VSCode.instance import InstanceDirectories


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


def test_adds_only_its_own_keywords_to_electron():
    added = set(import_library().get_keyword_names()) - set(Electron().get_keyword_names())

    assert added == {"Open VS Code", "Close VS Code", "Get VS Code Instance Directories"}


def test_instance_directories_of_the_active_instance(monkeypatch, tmp_path):
    vscode = import_library()
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "prepared")
    vscode._instances()["browser=open"] = Instance(tmp_path / "code", directories)

    result = vscode.get_vs_code_instance_directories()

    assert result == {
        "root": str(tmp_path),
        "user_data": str(tmp_path / "user-data"),
        "extensions": str(tmp_path / "prepared"),
    }
    assert result.extensions == str(tmp_path / "prepared")


def test_instance_directories_of_a_browser_not_opened_by_open_vs_code_fail():
    with pytest.raises(ValueError, match="'browser=unknown' is not an open VS Code instance"):
        import_library().get_vs_code_instance_directories("browser=unknown")


def test_instance_directories_of_a_closed_instance_fail(monkeypatch, tmp_path):
    vscode = import_library()
    monkeypatch.setattr(vscode, "get_browser_ids", lambda browser: ["browser=open"])
    directories = InstanceDirectories(tmp_path, tmp_path / "user-data", tmp_path / "extensions")
    instances = vscode._instances()
    instances["browser=open"] = instances["browser=closed"] = Instance(tmp_path / "code", directories)

    with pytest.raises(ValueError, match="'browser=closed' is not an open VS Code instance"):
        vscode.get_vs_code_instance_directories("browser=closed")
    assert list(vscode._instances()) == ["browser=open"]


def test_keeps_the_error_of_the_workbench_when_closing_fails(monkeypatch, tmp_path):
    executable = tmp_path / "code"
    executable.write_text("")
    executable.chmod(0o755)
    vscode = import_library()
    vscode.outputdir = str(tmp_path / "output")

    def not_ready(*args, **kwargs):
        raise TimeoutError("workbench not ready")

    def close_fails(*args, **kwargs):
        raise RuntimeError("closing failed")

    monkeypatch.setattr(vscode, "new_electron_application", lambda *args, **kwargs: ("browser", "context", {}))
    monkeypatch.setattr(vscode, "wait_for_elements_state", not_ready)
    monkeypatch.setattr(vscode, "close_browser", close_fails)

    with pytest.raises(TimeoutError, match="workbench not ready"):
        vscode.open_vs_code(executable=executable)
    assert vscode._instances() == {}


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


def test_intro_is_the_librarys_own_followed_by_browsers_sections():
    doc = LibraryDocumentation("VSCode").doc

    assert doc.startswith("VSCode library is a Robot Framework library for end-to-end testing of VS Code extensions.")
    assert "Browser library is a browser automation library" not in doc
    assert "= Assertions =" in doc


def test_import_is_documented_with_browsers_arguments():
    init = LibraryDocumentation("VSCode").inits[0]

    assert init.doc.startswith("VSCode library takes the same import arguments as the Browser library.")
    assert init.args.docs["timeout"].startswith("Timeout for keywords that operate on elements.")
    assert [arg.name for arg in init.args] == [arg.name for arg in LibraryDocumentation("Browser").inits[0].args]


def own_keywords(library: str) -> list[Any]:
    package = Path(inspect.getfile(VSCode)).parent
    return [kw for kw in LibraryDocumentation(library).keywords if Path(kw.source).is_relative_to(package)]


@pytest.mark.parametrize("library", ["VSCode", "VSCode.Helper"])
def test_own_keywords_document_every_argument_and_return_value(library):
    keywords = own_keywords(library)

    assert keywords
    for keyword in keywords:
        assert all(keyword.args.docs.get(arg.name) for arg in keyword.args if arg.name), keyword.name
        returns_nothing = keyword.args.return_type is None or keyword.args.return_type.type is type(None)
        assert returns_nothing or keyword.args.return_doc, keyword.name


@pytest.mark.parametrize(
    ("library", "name", "exceptions"),
    [
        ("VSCode", "Open VS Code", {"ValueError"}),
        ("VSCode", "Get VS Code Instance Directories", {"ValueError"}),
        ("VSCode.Helper", "Get VS Code Executable", {"ValueError"}),
        ("VSCode.Helper", "Execute VS Code CLI Command", {"ValueError", "RuntimeError"}),
    ],
)
def test_keywords_document_the_exceptions_for_invalid_input(library, name, exceptions):
    keyword = next(kw for kw in own_keywords(library) if kw.name == name)

    assert exceptions <= set(keyword.args.raises)
