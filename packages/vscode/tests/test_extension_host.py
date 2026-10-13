"""Choosing an extension host and evaluating in it, with fake helpers on 127.0.0.1."""

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from VSCode import extension_host
from VSCode.extension_host import (
    HELPER_EXTENSION,
    HELPER_ID,
    ExtensionHost,
    PageNotReadyError,
    UnknownWorkspaceError,
    endpoint_directory,
    live_extension_hosts,
    run_in_extension_host,
)

TOKEN = "secret"

Answer = Callable[[dict[str, Any]], dict[str, Any]]


class FakeHelper:
    """The helper of one extension host: a server that answers with ``answer`` and its endpoint file.

    ``probe`` replaces the answer to a probe, to fake another process on the helper's port.
    """

    def __init__(
        self,
        directory: Path,
        name: str,
        answer: Answer,
        workspace: str | None,
        workspace_id: str | None,
        probe: bytes | None = None,
    ):
        helper = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if probe is None:
                    self.reply({"pid": 1})
                else:
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(probe)))
                    self.end_headers()
                    self.wfile.write(probe)

            def do_POST(self) -> None:
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                helper.requests.append(body)
                self.reply(answer(body))

            def reply(self, payload: dict[str, Any]) -> None:
                status = 200 if self.headers.get("Authorization") == f"Bearer {TOKEN}" else 403
                text = json.dumps(payload if status == 200 else {"error": {"message": "no token"}}).encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(text)))
                self.end_headers()
                self.wfile.write(text)

            def log_message(self, *args: Any) -> None:
                pass

        self.requests: list[dict[str, Any]] = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        # Short polls and daemon threads let the tests shut the server down at once.
        self.server.daemon_threads = True
        # A client that gave up waiting is no error of the fake.
        self.server.handle_error = lambda request, client_address: None  # type: ignore[method-assign]
        threading.Thread(target=self.server.serve_forever, args=(0.01,), daemon=True).start()
        self.file = directory / f"{name}.json"
        endpoint = {"port": self.server.server_address[1], "token": TOKEN, "pid": 1}
        self.file.write_text(json.dumps({**endpoint, "workspace": workspace, "workspaceId": workspace_id}))


def answer_with(name: str) -> Answer:
    """Answers with the helper's name, the script and the argument, to show which host ran the function."""
    return lambda body: {"result": [name, body["script"], body["arg"]]}


@pytest.fixture
def user_data(tmp_path: Path) -> Path:
    path = tmp_path / "user-data"
    endpoint_directory(path).mkdir(parents=True)
    return path


@pytest.fixture
def add_helper(user_data) -> Iterator[Callable[..., FakeHelper]]:
    helpers: list[FakeHelper] = []

    def add(
        name: str,
        workspace: str | None = None,
        workspace_id: str | None = None,
        answer: Answer | None = None,
        probe: bytes | None = None,
    ) -> FakeHelper:
        directory = endpoint_directory(user_data)
        helper = FakeHelper(directory, name, answer or answer_with(name), workspace, workspace_id, probe)
        helpers.append(helper)
        return helper

    yield add
    for helper in helpers:
        helper.server.shutdown()
        helper.server.server_close()


def unreadable_page() -> str | None:
    raise UnknownWorkspaceError


def no_page() -> str | None:
    raise AssertionError("the active page was read although a workspace was given")


def run(
    user_data: Path, workspace: Path | None = None, page: Callable[[], str | None] = unreadable_page, timeout=2.0
) -> Any:
    return run_in_extension_host(user_data, "(vscode, arg) => arg", {"answer": 42}, workspace, page, timeout)


def test_helper_id_is_the_id_of_the_packaged_extension():
    package = json.loads((HELPER_EXTENSION / "package.json").read_text(encoding="utf-8"))

    assert HELPER_ID == "robotframework-vscode.extension-host" == f"{package['publisher']}.{package['name']}"


def test_evaluates_in_the_extension_host_of_the_active_pages_window(user_data, add_helper):
    add_helper("only", workspace="/work/a", workspace_id="id-a")

    assert run(user_data, page=lambda: "id-a") == ["only", "(vscode, arg) => arg", {"answer": 42}]


def test_waits_for_the_extension_host_of_the_active_pages_window_beside_another_one(user_data, add_helper):
    add_helper("a", workspace="/work/a", workspace_id="id-a")
    threading.Timer(0.5, lambda: add_helper("b", workspace="/work/b", workspace_id="id-b")).start()

    assert run(user_data, page=lambda: "id-b", timeout=5)[0] == "b"


def test_takes_the_only_extension_host_when_the_page_cannot_be_read(user_data, add_helper):
    add_helper("only", workspace="/work/a", workspace_id="id-a")

    assert run(user_data, page=unreadable_page)[0] == "only"


def test_fails_after_the_timeout_when_the_page_tells_no_workspace_and_there_are_several_windows(user_data, add_helper):
    add_helper("a", workspace="/work/a", workspace_id="id-a")
    add_helper("b", workspace="/work/b", workspace_id="id-b")
    started = time.monotonic()

    with pytest.raises(AssertionError) as error:
        run(user_data, page=unreadable_page, timeout=0.3)
    assert time.monotonic() - started >= 0.3
    assert str(error.value) == (
        "The active page's window could not be read within 300 milliseconds: it tells no workspace, and the "
        "VS Code instance has several windows. 'workspace' selects a window by its workspace."
    )


def test_chooses_the_extension_host_by_its_workspace(user_data, add_helper, tmp_path):
    add_helper("a", workspace=str(tmp_path / "a"))
    add_helper("b", workspace=str(tmp_path / "b"))

    assert run(user_data, workspace=tmp_path / "b", page=no_page)[0] == "b"


def test_compares_the_workspace_after_resolving_paths(user_data, add_helper, tmp_path, monkeypatch):
    (tmp_path / "a").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "a")
    add_helper("a", workspace=str(tmp_path / "link"))
    add_helper("b", workspace=str(tmp_path / "b"))
    monkeypatch.chdir(tmp_path)

    assert run(user_data, workspace=Path("b/../a"), page=no_page)[0] == "a"


def test_chooses_the_extension_host_of_the_active_pages_workspace(user_data, add_helper):
    add_helper("a", workspace="/work/a", workspace_id="id-a")
    add_helper("b", workspace=None, workspace_id="id-b")

    assert run(user_data, page=lambda: "id-b")[0] == "b"


def test_chooses_the_only_window_without_a_workspace_for_such_a_page(user_data, add_helper):
    add_helper("a", workspace="/work/a", workspace_id="id-a")
    add_helper("empty")

    assert run(user_data, page=lambda: None)[0] == "empty"


def test_fails_at_once_when_several_windows_have_no_workspace(user_data, add_helper):
    add_helper("first")
    add_helper("second")
    started = time.monotonic()

    with pytest.raises(AssertionError, match="The window of the active page cannot be determined"):
        run(user_data, page=lambda: None, timeout=5)
    assert time.monotonic() - started < 1


def free_port() -> int:
    with socket.socket() as unused:
        unused.bind(("127.0.0.1", 0))
        port: int = unused.getsockname()[1]
    return port


def test_ignores_and_deletes_the_endpoint_files_of_ended_extension_hosts(user_data, add_helper):
    ended = endpoint_directory(user_data) / "ended.json"
    endpoint = {"pid": 1, "port": free_port(), "token": TOKEN, "workspace": None, "workspaceId": None}
    ended.write_text(json.dumps(endpoint))
    other_token = add_helper("process that does not know the token")
    other_token.file.write_text(other_token.file.read_text().replace(TOKEN, "another token"))
    other_process = add_helper("process with another pid")
    other_process.file.write_text(other_process.file.read_text().replace('"pid": 1', '"pid": 2'))
    add_helper("process that answers no json", probe=b"<html></html>")
    add_helper("live")

    assert [host.file.stem for host in live_extension_hosts(user_data)] == ["live"]
    assert sorted(file.stem for file in endpoint_directory(user_data).iterdir()) == ["live"]


def test_ignores_files_that_are_being_written(user_data, add_helper):
    (endpoint_directory(user_data) / "half.json.tmp").write_text("{")
    add_helper("complete")

    assert run(user_data)[0] == "complete"


def test_waits_for_the_extension_host(user_data, add_helper):
    threading.Timer(0.5, lambda: add_helper("late")).start()

    assert run(user_data, timeout=5)[0] == "late"


def test_names_the_workspace_and_the_open_workspaces_after_the_timeout(user_data, add_helper):
    add_helper("a", workspace="/work/a")
    add_helper("empty")
    started = time.monotonic()

    with pytest.raises(AssertionError) as error:
        run(user_data, workspace=Path("/nowhere"), page=no_page, timeout=0.3)
    assert time.monotonic() - started >= 0.3
    assert str(error.value) == (
        "No window of the VS Code instance has the workspace '/nowhere' open within 300 milliseconds. "
        "Open workspaces: '/work/a', a window without a workspace path."
    )


def test_fails_after_the_timeout_without_an_extension_host(user_data):
    with pytest.raises(AssertionError, match=r"^No extension host of the VS Code instance answered within 200"):
        run(user_data, timeout=0.2)


def test_fails_after_the_timeout_without_the_extension_host_of_the_active_page(user_data, add_helper):
    add_helper("a", workspace="/work/a", workspace_id="id-a")
    add_helper("b", workspace="/work/b", workspace_id="id-b")
    reads: list[str] = []

    def page() -> str:
        reads.append("id-c")
        return "id-c"

    with pytest.raises(AssertionError, match=r"^The extension host of the active page's window did not answer"):
        run(user_data, page=page, timeout=0.3)
    assert reads == ["id-c"]


def test_fails_with_the_error_message_of_the_function(user_data, add_helper):
    add_helper("broken", answer=lambda body: {"error": {"message": "broken", "stack": "Error: broken\n    at ..."}})

    with pytest.raises(AssertionError, match=r"^broken$"):
        run(user_data)


def test_fails_when_the_function_does_not_finish_in_time(user_data, add_helper):
    def slow(body: dict[str, Any]) -> dict[str, Any]:
        time.sleep(1)
        return {"result": None}

    add_helper("slow", answer=slow)

    with pytest.raises(AssertionError, match=r"^The function did not finish within 300 milliseconds"):
        run(user_data, timeout=0.3)


def test_reaches_the_extension_host_despite_a_proxy(user_data, add_helper):
    add_helper("direct")
    # A fresh interpreter, so that the proxy is set before the module creates its opener.
    proxy = f"http://127.0.0.1:{free_port()}"
    env = {**os.environ, "http_proxy": proxy, "HTTP_PROXY": proxy, "no_proxy": "", "NO_PROXY": ""}
    code = (
        "import sys; from pathlib import Path; from VSCode.extension_host import live_extension_hosts; "
        "print([host.file.stem for host in live_extension_hosts(Path(sys.argv[1]))])"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code, str(user_data)], env=env, capture_output=True, text=True, check=True, timeout=30
    )

    assert completed.stdout.strip() == "['direct']"


def test_reads_the_page_again_while_the_window_reloads(user_data, add_helper):
    add_helper("a", workspace_id="id-a")
    add_helper("b", workspace_id="id-b")
    reads: list[str] = []

    def page() -> str:
        reads.append("read")
        if len(reads) < 3:
            raise PageNotReadyError("Execution context was destroyed")
        return "id-b"

    assert run(user_data, page=page)[0] == "b"
    assert reads == ["read", "read", "read"]


def test_names_the_error_of_the_page_after_the_timeout(user_data, add_helper):
    add_helper("a", workspace_id="id-a")

    def page() -> str:
        raise PageNotReadyError("Execution context was destroyed")

    with pytest.raises(AssertionError) as error:
        run(user_data, page=page, timeout=0.2)
    assert str(error.value) == (
        "The active page's window could not be read within 200 milliseconds: Execution context was destroyed"
    )


def test_waits_for_the_next_extension_host_when_one_ends_before_it_gets_the_function(
    user_data, add_helper, monkeypatch
):
    ended = endpoint_directory(user_data) / "ended.json"
    ended.write_text("{}")
    add_helper("next")
    probes = [[ExtensionHost(ended, 1, free_port(), TOKEN, None, None)]]

    def live(user_data: Path) -> list[ExtensionHost]:
        return probes.pop() if probes else live_extension_hosts(user_data)

    monkeypatch.setattr(extension_host, "live_extension_hosts", live)

    assert run(user_data)[0] == "next"
    assert not ended.exists()


def test_fails_at_once_for_an_argument_that_is_no_json(user_data):
    started = time.monotonic()

    with pytest.raises(ValueError, match=r"^'arg' cannot be serialised as JSON: "):
        run_in_extension_host(user_data, "(vscode, arg) => arg", object(), None, unreadable_page, 5)
    assert time.monotonic() - started < 1


def test_fails_at_once_for_an_argument_that_json_has_no_number_for(user_data):
    with pytest.raises(ValueError, match=r"^'arg' cannot be serialised as JSON: Out of range float values"):
        run_in_extension_host(user_data, "(vscode, arg) => arg", float("nan"), None, unreadable_page, 5)


@pytest.mark.parametrize(
    ("error", "kept"),
    [
        (urllib.error.URLError(TimeoutError("timed out")), False),  # no connection: nothing listens on the port
        (TimeoutError("timed out"), True),  # connected, but no answer: busy
    ],
)
def test_tells_ended_extension_hosts_from_busy_ones(user_data, add_helper, monkeypatch, error, kept):
    helper = add_helper("host")

    def send(self, method: str, body: bytes | None, timeout: float) -> Any:
        raise error

    monkeypatch.setattr(ExtensionHost, "send", send)

    assert live_extension_hosts(user_data) == []
    assert helper.file.exists() is kept


def test_names_a_busy_extension_host_of_the_workspace_after_the_timeout(user_data, add_helper, monkeypatch):
    monkeypatch.setattr(extension_host, "_PROBE_TIMEOUT", 0.1)

    def busy(body: dict[str, Any]) -> dict[str, Any]:
        return {"result": None}

    helper = add_helper("busy", workspace="/work/busy", answer=busy)
    helper.server.RequestHandlerClass.do_GET = lambda handler: time.sleep(0.5)

    with pytest.raises(AssertionError) as error:
        run(user_data, workspace=Path("/work/busy"), page=no_page, timeout=0.3)
    assert str(error.value) == (
        "The extension host of the workspace '/work/busy' did not answer within 300 milliseconds. "
        "A function that has not finished may keep it busy."
    )
