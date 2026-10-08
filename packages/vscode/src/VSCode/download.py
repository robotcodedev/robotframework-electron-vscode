"""Resolving, downloading and caching VS Code builds."""

import hashlib
import json
import os
import platform
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple

from Electron.Helper import extract_zip, user_cache_dir

UPDATE_SERVICE = "https://update.code.visualstudio.com"
LATEST = {"stable": "stable", "insiders": "insider", "insider": "insider"}


class Build(NamedTuple):
    quality: str
    """``stable`` or ``insider``, as the update service names them."""
    version: str
    """The product version, for example ``1.141.0`` or ``1.142.0-insider``."""
    url: str
    sha256: str


class CachedBuild(NamedTuple):
    folder: Path
    quality: str
    version: str


def vscode_platform(system: str = sys.platform, machine: str = platform.machine()) -> str:
    """Return the update service's platform name, for example ``linux-x64``."""
    arm = machine.lower() in ("arm64", "aarch64")
    if system == "linux":
        return "linux-arm64" if arm else "linux-x64"
    if system == "win32":
        return "win32-arm64-archive" if arm else "win32-x64-archive"
    if system == "darwin":
        return "darwin-arm64" if arm else "darwin"
    raise ValueError(f"VS Code builds are not available for platform '{system}'.")


def default_cache_dir() -> Path:
    """Return the user's cache directory for VS Code builds."""
    return user_cache_dir() / "robotframework-vscode" / "vscode"


def _open(url: str):
    return urllib.request.urlopen(url)


def _quality_of(version: str) -> str:
    return "insider" if version.endswith("-insider") else "stable"


def resolve_build(version: str, platform_name: str) -> Build:
    """Ask the update service for the build of ``version`` (``stable``, ``insiders`` or a version)."""
    quality = LATEST.get(version.lower())
    if quality:
        url = f"{UPDATE_SERVICE}/api/update/{platform_name}/{quality}/latest"
    else:
        quality = _quality_of(version)
        url = f"{UPDATE_SERVICE}/api/versions/{version}/{platform_name}/{quality}"
    try:
        with _open(url) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise ValueError(f"VS Code version '{version}' not found for {platform_name} ({error.code}).") from error
    if not body:
        raise ValueError(f"VS Code version '{version}' not found for {platform_name}.")
    data = json.loads(body)
    return Build(quality, data["productVersion"], data["url"], data["sha256hash"])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract(archive: Path, target: Path) -> Path:
    """Extract a build archive and return the folder that holds the build."""
    if archive.name.endswith(".tar.gz"):
        with tarfile.open(archive) as tar:
            if hasattr(tarfile, "tar_filter"):
                tar.extractall(target, filter="tar")
            else:  # Python < 3.12
                tar.extractall(target)
    else:
        extract_zip(archive, target)
    entries = list(target.iterdir())
    # The Linux archive wraps the build in one folder (VSCode-linux-x64); a macOS .app is the build.
    if len(entries) == 1 and entries[0].is_dir() and entries[0].suffix != ".app":
        return entries[0]
    return target


def _cache_folder(cache_dir: Path, quality: str, version: str, platform_name: str) -> Path:
    return cache_dir / f"{quality}-{version}-{platform_name}"


def download_vscode(version: str, cache_dir: Path) -> CachedBuild:
    """Return the cached build of ``version``, downloading it first if needed.

    A fixed version that is already cached is returned without network access.
    """
    platform_name = vscode_platform()
    if version.lower() not in LATEST:
        quality = _quality_of(version)
        folder = _cache_folder(cache_dir, quality, version, platform_name)
        if folder.is_dir():
            return CachedBuild(folder, quality, version)
    build = resolve_build(version, platform_name)
    folder = _cache_folder(cache_dir, build.quality, build.version, platform_name)
    cached = CachedBuild(folder, build.quality, build.version)
    if folder.is_dir():
        return cached
    cache_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache_dir) as tmp:
        archive = Path(tmp, "build.tar.gz" if build.url.endswith(".tar.gz") else "build.zip")
        with _open(build.url) as response, open(archive, "wb") as file:
            shutil.copyfileobj(response, file)
        actual = _sha256(archive)
        if actual != build.sha256:
            raise ValueError(f"Checksum mismatch for VS Code {build.version}: got {actual}, expected {build.sha256}.")
        root = _extract(archive, Path(tmp, "extracted"))
        try:
            os.replace(root, folder)
        except OSError:
            if not folder.is_dir():  # another process may have won the race
                raise
    return cached


def executable_path(folder: Path, quality: str, system: str = sys.platform) -> Path:
    """Return the VS Code executable inside a build folder."""
    insider = quality == "insider"
    if system == "win32":
        return folder / ("Code - Insiders.exe" if insider else "Code.exe")
    if system == "darwin":
        apps = sorted(folder.glob("*.app"))
        if not apps:
            raise ValueError(f"No VS Code application bundle found in {folder}.")
        binaries = apps[0] / "Contents" / "MacOS"
        for name in ("Code", "Electron", "Code - Insiders"):
            if (binaries / name).is_file():
                return binaries / name
        return next(binaries.iterdir())
    return folder / ("code-insiders" if insider else "code")


def _app_folder(executable: Path, system: str) -> Path:
    if system == "darwin":
        return executable.parents[1] / "Resources" / "app"
    return executable.parent / "resources" / "app"


def cli_path(executable: Path, system: str = sys.platform) -> Path:
    """Return the VS Code command-line script that belongs to ``executable``."""
    if system == "darwin":
        bin_dir = _app_folder(executable, system) / "bin"
        names = ["code", "code-insiders"]
    else:
        bin_dir = executable.parent / "bin"
        names = ["code.cmd", "code-insiders.cmd"] if system == "win32" else ["code", "code-insiders"]
    for name in names:
        if (bin_dir / name).is_file():
            return bin_dir / name
    raise ValueError(f"No VS Code command-line script found in {bin_dir}.")


def product_version(executable: Path, system: str = sys.platform) -> str | None:
    """Return the version of the VS Code that ``executable`` belongs to, if it can be found."""
    package = _app_folder(executable, system) / "package.json"
    try:
        return json.loads(package.read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None
