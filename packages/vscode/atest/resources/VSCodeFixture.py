"""Test helper for the VSCode acceptance tests: instance folders, processes and extension packages."""

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from VSCode.extension_host import endpoint_directory
from VSCode.instance import instance_environment


def newest_instance_directory(output_dir: str) -> str:
    """Return the instance folder that `Open VS Code` created last in ``output_dir``."""
    base = Path(output_dir) / "vscode"
    return str(base / str(max(int(entry.name) for entry in base.iterdir() if entry.name.isdigit())))


def count_processes_with(text: str) -> int:
    """Count running processes whose command line contains ``text``."""
    result = subprocess.run(["pgrep", "-f", "--", re.escape(text)], capture_output=True, text=True, check=False)
    return len(result.stdout.split())


def list_user_extensions() -> list[str]:
    """Return the extension folders of the user's own VS Code."""
    folder = Path.home() / ".vscode" / "extensions"
    return sorted(entry.name for entry in folder.iterdir()) if folder.is_dir() else []


_VSIX_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}" />
    <DisplayName>{display_name}</DisplayName>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{engine}" />
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code" /></Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""

_VSIX_CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json" />
  <Default Extension=".js" ContentType="application/javascript" />
  <Default Extension=".vsixmanifest" ContentType="text/xml" />
</Types>
"""


def pack_extension(folder: str, target: str) -> str:
    """Pack the extension in ``folder`` into the ``.vsix`` file ``target``, without vsce."""
    source = Path(folder)
    package = json.loads((source / "package.json").read_text(encoding="utf-8"))
    manifest = _VSIX_MANIFEST.format(
        name=package["name"],
        version=package["version"],
        publisher=package["publisher"],
        display_name=package.get("displayName", package["name"]),
        engine=package["engines"]["vscode"],
    )
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as vsix:
        vsix.writestr("[Content_Types].xml", _VSIX_CONTENT_TYPES)
        vsix.writestr("extension.vsixmanifest", manifest)
        for file in sorted(path for path in source.rglob("*") if path.is_file()):
            vsix.write(file, f"extension/{file.relative_to(source).as_posix()}")
    return target


def send_evaluation_without_token(user_data_dir: str, function: str) -> list[int]:
    """Send ``function`` to the helper in every extension host of an instance without the token.

    Returns the HTTP status of each answer.
    """
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    statuses = []
    for file in sorted(endpoint_directory(Path(user_data_dir)).glob("*.json")):
        port = json.loads(file.read_text(encoding="utf-8"))["port"]
        body = json.dumps({"script": function, "arg": None}).encode("utf-8")
        request = urllib.request.Request(f"http://127.0.0.1:{port}/", data=body, method="POST")
        try:
            with opener.open(request, timeout=10) as response:
                statuses.append(response.status)
        except urllib.error.HTTPError as error:
            statuses.append(error.code)
    return statuses


def vs_code_environment() -> dict[str, str]:
    """Return the environment for a VS Code that `New Electron Application` starts, as `Open VS Code` uses it."""
    return instance_environment(os.environ)


def process_should_have_exited(pid: int) -> None:
    """Fail while the process ``pid`` is still running. For Linux and macOS, like ``count_processes_with``."""
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return
    raise AssertionError(f"Process {pid} is still running.")
