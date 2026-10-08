"""Test helper for the VSCode acceptance tests: instance folders, processes and extension packages."""

import json
import subprocess
import zipfile
from pathlib import Path


def newest_instance_directory(output_dir: str) -> str:
    """Return the instance folder that `Open VS Code` created last in ``output_dir``."""
    base = Path(output_dir) / "vscode"
    return str(base / str(max(int(entry.name) for entry in base.iterdir() if entry.name.isdigit())))


def count_processes_with(text: str) -> int:
    """Count running processes whose command line contains ``text``."""
    result = subprocess.run(["pgrep", "-f", "--", text], capture_output=True, text=True, check=False)
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
