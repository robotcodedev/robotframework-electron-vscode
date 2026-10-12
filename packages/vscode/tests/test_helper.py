from pathlib import Path
from typing import Any

import pytest
from Browser import playwright

import Electron.Helper
from VSCode import VSCode
from VSCode.download import SelectedBuild
from VSCode.Helper import Helper


@pytest.fixture(autouse=True)
def _isolated_cwd(tmp_path, monkeypatch):
    # Browser deletes ./playwright-log.txt when it is created outside a run.
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def no_network(monkeypatch):
    def fail(url):
        raise AssertionError(f"network access to {url}")

    monkeypatch.setattr(Electron.Helper, "open_url", fail)


def test_returns_given_executable_without_downloading(no_network, tmp_path):
    executable = Helper().get_vs_code_executable("stable", Path("/usr/share/code/code"), tmp_path)

    assert executable == str(Path("/usr/share/code/code"))
    assert list(tmp_path.iterdir()) == []


def test_vscode_library_no_longer_downloads_on_its_own():
    assert "Download VS Code" not in VSCode().get_keyword_names()


def test_cli_runs_the_script_of_the_selected_build_without_vs_code_variables_or_node(tmp_path, monkeypatch):
    calls: list[dict[str, Any]] = []

    def run_cli(cli: Path, ext: Path, data: Path, args: tuple[str, ...], env: dict[str, str]) -> str:
        calls.append({"cli": cli, "args": args, "env": env})
        return "listed\n"

    monkeypatch.setattr("VSCode.Helper.select_build", lambda *args: SelectedBuild(tmp_path / "code", "1.141.0"))
    monkeypatch.setattr("VSCode.Helper.cli_path", lambda executable: executable.parent / "bin" / "code")
    monkeypatch.setattr("VSCode.Helper.run_cli", run_cli)
    monkeypatch.setenv("VSCODE_IPC_HOOK_CLI", "/tmp/vscode-ipc.sock")
    monkeypatch.setenv("ELECTRON_RUN_AS_NODE", "1")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise AssertionError(f"process started: {args}")

    monkeypatch.setattr(playwright, "Popen", fail)
    monkeypatch.setattr(playwright, "run", fail)

    output = Helper().execute_vs_code_cli_command(Path("ext"), Path("data"), "--list-extensions", version="1.141.0")

    [call] = calls
    assert output == "listed\n"
    assert call["cli"] == tmp_path / "bin" / "code"
    assert call["args"] == ("--list-extensions",)
    assert "VSCODE_IPC_HOOK_CLI" not in call["env"]
    assert "ELECTRON_RUN_AS_NODE" not in call["env"]
