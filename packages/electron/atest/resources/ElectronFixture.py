"""Test helper for the Electron acceptance tests: the fixture app and its processes."""

import json
import re
import subprocess
import tempfile
import threading
import time
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast

from robot.libraries.BuiltIn import BuiltIn

from Electron import Electron

FIXTURE_APP = Path(__file__).resolve().parent.parent / "fixtures" / "app"


def get_fixture_app() -> str:
    """Return the path of the Electron fixture app."""
    return str(FIXTURE_APP)


def new_user_data_dir(output_dir: str) -> str:
    """Create a new, empty user-data directory for one start of the fixture app under ``output_dir``."""
    base = Path(output_dir) / "electron-user-data"
    base.mkdir(parents=True, exist_ok=True)
    return tempfile.mkdtemp(dir=base)


def count_fixture_app_processes(marker: str) -> int:
    """Count running processes whose command line contains the fixture app path and ``marker``.

    Chromium moves switches in front of positional arguments in its command
    line, so both orders are matched.
    """
    app, marker = re.escape(str(FIXTURE_APP)), re.escape(marker)
    pattern = f"{app}.*{marker}|{marker}.*{app}"
    result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True, check=False)
    return len(result.stdout.split())


_PAGE = b"""<!doctype html>
<button id="load">Load</button>
<div id="result"></div>
<a id="slow" href="/slow">Slow download</a>
<script>
document.getElementById("load").onclick = () =>
    fetch("/api")
        .then((response) => response.text())
        .then((text) => (document.getElementById("result").textContent = text));
</script>
"""


# The download of /slow takes 20 seconds, long enough for a test to cancel it.
_SLOW_CHUNKS = 200
_SLOW_CHUNK = b"x" * 1024


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/slow":
            self._send_slowly()
            return
        body, content_type = (b'{"answer": 42}', "application/json") if self.path == "/api" else (_PAGE, "text/html")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_slowly(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Disposition", 'attachment; filename="slow.bin"')
        self.send_header("Content-Length", str(_SLOW_CHUNKS * len(_SLOW_CHUNK)))
        self.end_headers()
        for _ in range(_SLOW_CHUNKS):
            try:
                self.wfile.write(_SLOW_CHUNK)
                self.wfile.flush()
            except OSError:  # The download was cancelled.
                return
            time.sleep(0.1)

    def log_message(self, *args: Any) -> None:
        pass


_server: ThreadingHTTPServer | None = None


def web_server_url() -> str:
    """Return the URL of a local web server with a page that loads ``/api``, starting it on first use."""
    global _server
    if _server is None:
        _server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_server.server_address[1]}/"


def register_tag_selector_engine() -> None:
    """Register the custom selector engine ``tag`` of ``selector_engine.js`` in Browser's Node process."""
    electron = cast(Electron, BuiltIn().get_library_instance("Electron"))
    electron.init_js_extension(str(Path(__file__).with_name("selector_engine.js")))
    electron.call_js_keyword("fixtureRegisterTagEngine")


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
