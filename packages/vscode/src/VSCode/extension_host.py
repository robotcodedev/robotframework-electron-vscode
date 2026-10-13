"""The library's helper extension in VS Code's extension hosts, and evaluating functions through it."""

import functools
import http.client
import importlib.metadata
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

from packaging.version import InvalidVersion, Version
from robot.api import logger
from robot.utils import secs_to_timestr

# The helper extension, which a test loads as a development extension, or installs from its .vsix.
HELPER_EXTENSION = Path(__file__).with_name("extension")
# The package's build packs it; a source checkout has it only after `uv build`.
HELPER_VSIX = Path(__file__).with_name("extension-host.vsix")

_PACKAGE = json.loads((HELPER_EXTENSION / "package.json").read_text(encoding="utf-8"))
# VS Code's id of the helper, which names its folder in the global storage.
HELPER_ID = f"{_PACKAGE['publisher']}.{_PACKAGE['name']}"
# The helper has the library's version, as a semantic version such as 0.2.0-dev.12 for 0.2.0.dev12.
LIBRARY_VERSION = importlib.metadata.version("robotframework-vscode")

# Reads VS Code's id of the workspace of the active page's workbench window. A window into
# which an editor was moved belongs to the workbench window that opened it. A window that has
# just opened gets its configuration a moment after its page exists, so the script waits for it.
PAGE_WORKSPACE_ID = """async () => {
    const configuration = async (target) => {
        try {
            const context = target?.vscode?.context;
            return context?.resolveConfiguration ? await context.resolveConfiguration() : context?.configuration?.();
        } catch {
            return undefined;
        }
    };
    const found = (await configuration(window)) ?? (await configuration(window.opener));
    return found ? { workspaceId: found.workspace?.id ?? null } : null;
}"""

# How long a probe waits for an extension host, which is busy if it does not answer by then.
_PROBE_TIMEOUT = 1.0
_POLL_INTERVAL = 0.1

# Requests go to 127.0.0.1 directly, also when the environment configures a proxy.
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class UnknownWorkspaceError(Exception):
    """The active page is no workbench window, or VS Code changed the internals that tell its workspace."""


class PageNotReadyError(Exception):
    """The active page cannot be read for the moment, for example while the window reloads."""


class _ExtensionHostEndedError(Exception):
    """No connection came about, so the extension host ended before it got the function."""


class ExtensionHost(NamedTuple):
    """The helper in one extension host, as its endpoint file describes it."""

    file: Path
    pid: int
    port: int
    token: str
    workspace: str | None
    workspace_id: str | None
    version: str | None = None

    def send(self, method: str, body: bytes | None, timeout: float) -> Any:
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/",
            data=body,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
        )
        with _OPENER.open(request, timeout=timeout) as response:
            return json.loads(response.read())


def endpoint_directory(user_data: Path) -> Path:
    """Return the folder in which the helper writes an endpoint file per extension host."""
    return user_data / "User" / "globalStorage" / HELPER_ID / "hosts"


def read_extension_hosts(user_data: Path) -> list[ExtensionHost]:
    """Return the extension hosts whose endpoint files are in the user-data directory ``user_data``."""
    hosts = []
    for file in sorted(endpoint_directory(user_data).glob("*.json")):
        try:
            endpoint = json.loads(file.read_text(encoding="utf-8"))
            hosts.append(
                ExtensionHost(
                    file,
                    endpoint["pid"],
                    endpoint["port"],
                    endpoint["token"],
                    endpoint["workspace"],
                    endpoint["workspaceId"],
                    endpoint.get("version"),
                )
            )
        except (OSError, ValueError, KeyError, TypeError):
            continue  # removed in the meantime, or not an endpoint file
    return hosts


def live_extension_hosts(user_data: Path) -> list[ExtensionHost]:
    """Return the extension hosts that answer a probe, and delete the endpoint files of ended ones."""
    live = []
    for host in read_extension_hosts(user_data):
        try:
            answer = host.send("GET", None, _PROBE_TIMEOUT)
        except (urllib.error.HTTPError, http.client.HTTPException, ValueError):
            answer = None  # another process listens on the port, which does not know the token
        except urllib.error.URLError as error:
            if not _not_connected(error):
                continue
            answer = None
        except OSError:
            continue  # connected, but busy, for example with a long synchronous function
        if isinstance(answer, dict) and answer.get("pid") == host.pid:
            live.append(host)
        else:
            host.file.unlink(missing_ok=True)
    return live


def _not_connected(error: urllib.error.URLError) -> bool:
    """Tell whether ``error`` means that no connection came about, so that no extension host listens on the port.

    Windows reports a refused connection on 127.0.0.1 only after a while, so a timeout while connecting means the
    same. A busy extension host still accepts the connection and only answers late.
    """
    return isinstance(error.reason, (ConnectionRefusedError, TimeoutError))


def _comparable(path: str | Path) -> str:
    resolved = os.path.realpath(path)
    return resolved.casefold() if sys.platform in ("win32", "darwin") else resolved


def choose_extension_host(
    hosts: list[ExtensionHost], workspace: Path | None, page_workspace_id: Callable[[], str | None]
) -> ExtensionHost | None:
    """Return the host with the workspace ``workspace``, or the one of the active page's window.

    ``page_workspace_id`` returns VS Code's id of the workspace of the active page's window, or raises
    `UnknownWorkspaceError`. Then the only host is taken, and with several hosts the page is read again.
    """
    if workspace is not None:
        wanted = _comparable(workspace)
        return next((host for host in hosts if host.workspace and _comparable(host.workspace) == wanted), None)
    try:
        workspace_id = page_workspace_id()
    except UnknownWorkspaceError:
        if len(hosts) > 1:
            # Early in a reload, the page may not know its workspace yet.
            raise PageNotReadyError(
                "it tells no workspace, and the VS Code instance has several windows. 'workspace' selects a window "
                "by its workspace."
            ) from None
        return hosts[0] if hosts else None
    candidates = [host for host in hosts if host.workspace_id == workspace_id]
    if workspace_id is None and len(candidates) > 1:
        raise AssertionError(
            "The window of the active page cannot be determined: several windows of the VS Code instance "
            "have no workspace. 'workspace' selects a window by its workspace."
        )
    return candidates[0] if candidates else None


def _workspaces(hosts: list[ExtensionHost]) -> str:
    return ", ".join(f"'{host.workspace}'" if host.workspace else "a window without a workspace path" for host in hosts)


def _not_found(
    user_data: Path,
    workspace: Path | None,
    hosts: list[ExtensionHost],
    page_error: PageNotReadyError | None,
    timeout: float,
) -> str:
    within = f"within {secs_to_timestr(timeout)}"
    if workspace is not None:
        wanted = _comparable(workspace)
        # Endpoint files of busy extension hosts stay, those of ended ones are deleted.
        if any(host.workspace and _comparable(host.workspace) == wanted for host in read_extension_hosts(user_data)):
            return (
                f"The extension host of the workspace '{workspace}' did not answer {within}. A function that has "
                "not finished may keep it busy."
            )
        message = f"No window of the VS Code instance has the workspace '{workspace}' open {within}."
        return f"{message} Open workspaces: {_workspaces(hosts) or 'none'}."
    if page_error is not None:
        return f"The active page's window could not be read {within}: {page_error}"
    if not hosts:
        return (
            f"No extension host of the VS Code instance answered {within}. The library's helper extension may not "
            f"be loaded: give its folder '{HELPER_EXTENSION}' to Open VS Code in extension_development_path, or "
            f"install '{HELPER_VSIX}' into the extensions directory before the start."
        )
    return (
        f"The extension host of the active page's window did not answer {within}. Open workspaces: "
        f"{_workspaces(hosts)}. 'workspace' selects a window by its workspace."
    )


def _check_version(host: ExtensionHost) -> None:
    """Fail when the helper in ``host`` comes from another version of the library, such as an old installed one."""
    try:
        same = host.version is not None and Version(host.version) == Version(LIBRARY_VERSION)
    except InvalidVersion:
        same = False
    if not same:
        raise AssertionError(
            f"The helper extension in this VS Code has the version {host.version or 'unknown'}, but the library has "
            f"{LIBRARY_VERSION}. Install '{HELPER_VSIX}' of this version of the library into the extensions directory "
            f"again, or load its folder '{HELPER_EXTENSION}' as a development extension."
        )


def send_function(host: ExtensionHost, body: bytes, timeout: float) -> Any:
    """Run the function in ``body`` in the extension host ``host`` and return its result."""
    try:
        answer = host.send("POST", body, timeout)
    except (TimeoutError, urllib.error.URLError, http.client.HTTPException, ConnectionError) as error:
        if isinstance(error, urllib.error.URLError) and _not_connected(error):
            raise _ExtensionHostEndedError from None
        reason = error.reason if isinstance(error, urllib.error.URLError) else error
        message = (
            f"The function did not finish within {secs_to_timestr(timeout)}. It keeps running in the extension host."
            if isinstance(reason, TimeoutError)
            else f"The extension host ended before the function finished: {reason}"
        )
        raise AssertionError(message) from None
    if "error" in answer:
        if "stack" in answer["error"]:
            logger.debug(answer["error"]["stack"])
        raise AssertionError(answer["error"]["message"])
    return answer["result"]


def run_in_extension_host(
    user_data: Path,
    script: str,
    arg: Any,
    workspace: Path | None,
    page_workspace_id: Callable[[], str | None],
    timeout: float,
) -> Any:
    """Run the function ``script`` with ``arg`` in the extension host that `choose_extension_host` chooses.

    Waits up to ``timeout`` seconds for that extension host, and then again for the function. ``page_workspace_id``
    may raise `PageNotReadyError`; the page is then read again.
    """
    try:
        body = json.dumps({"script": script, "arg": arg}, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ValueError(f"'arg' cannot be serialised as JSON: {error}") from None
    # The workspace of the page stays the same while the keyword waits, so the page is read once.
    page_workspace_id = functools.cache(page_workspace_id)
    deadline = time.monotonic() + timeout
    while True:
        hosts = live_extension_hosts(user_data)
        page_error = None
        try:
            host = choose_extension_host(hosts, workspace, page_workspace_id)
        except PageNotReadyError as error:
            host, page_error = None, error
        if host is not None:
            _check_version(host)
            where = f"workspace '{host.workspace}'" if host.workspace else "a window without a workspace path"
            logger.info(f"Running the function in the extension host of process {host.pid}, {where}.")
            try:
                return send_function(host, body, timeout)
            except _ExtensionHostEndedError:
                # Nothing ran, so the function can go to the extension host that comes next, after a reload.
                host.file.unlink(missing_ok=True)
        if time.monotonic() >= deadline:
            raise AssertionError(_not_found(user_data, workspace, hosts, page_error, timeout))
        time.sleep(_POLL_INTERVAL)
