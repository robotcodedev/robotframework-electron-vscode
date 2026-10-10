"""Test helper for the Electron acceptance tests: the fixture app and its processes."""

import json
import subprocess
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FIXTURE_APP = Path(__file__).resolve().parent.parent / "fixtures" / "app"


def get_fixture_app() -> str:
    """Return the path of the Electron fixture app."""
    return str(FIXTURE_APP)


def count_fixture_app_processes(marker: str) -> int:
    """Count running processes whose command line contains the fixture app path and ``marker``.

    Chromium moves switches in front of positional arguments in its command
    line, so both orders are matched.
    """
    pattern = f"{FIXTURE_APP}.*{marker}|{marker}.*{FIXTURE_APP}"
    result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    return len(result.stdout.split())


_PAGE = b"""<!doctype html>
<button id="load">Load</button>
<div id="result"></div>
<script>
document.getElementById("load").onclick = () =>
    fetch("/api").then((response) => response.text()).then((text) => (document.getElementById("result").textContent = text));
</script>
"""


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body, content_type = (b'{"answer": 42}', "application/json") if self.path == "/api" else (_PAGE, "text/html")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


_server: ThreadingHTTPServer | None = None


def web_server_url() -> str:
    """Return the URL of a local web server with a page that loads ``/api``, starting it on first use."""
    global _server  # noqa: PLW0603
    if _server is None:
        _server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_server.server_address[1]}/"


def read_trace(path: str) -> dict[str, list[str]]:
    """Return the Playwright actions and the keywords of the groups in a trace file.

    A group's title is the keyword name followed by its arguments, separated by no-break spaces.
    """
    with zipfile.ZipFile(path) as trace:
        events = [json.loads(line) for line in trace.read("trace.trace").decode().splitlines() if line.strip()]
    calls = [event for event in events if event.get("type") == "before"]
    return {
        "actions": [call["method"] for call in calls if call.get("method") != "tracingGroup"],
        "groups": [call.get("title", "").split("\xa0")[0] for call in calls if call.get("method") == "tracingGroup"],
    }
