"""Resolving, downloading and caching VS Code builds."""

import json
import os
import platform
import re
import shutil
import sys
import tempfile
import urllib.error
from pathlib import Path
from typing import NamedTuple

# Imported as a module, so that tests can replace Electron.Helper.open_url for both downloads.
import Electron.Helper
from Electron.Helper import architecture, download, extract_tar, extract_zip, sha256, user_cache_dir

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
    if system not in ("linux", "win32", "darwin"):
        raise ValueError(f"VS Code builds are not available for platform '{system}'.")
    arm = architecture(machine, "VS Code") == "arm64"
    if system == "linux":
        return "linux-arm64" if arm else "linux-x64"
    if system == "win32":
        return "win32-arm64-archive" if arm else "win32-x64-archive"
    return "darwin-arm64" if arm else "darwin"


def default_cache_dir() -> Path:
    """Return the user's cache directory for VS Code builds."""
    return user_cache_dir() / "robotframework-vscode" / "vscode"


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
        with Electron.Helper.open_url(url) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise ValueError(f"VS Code version '{version}' not found for {platform_name} ({error.code}).") from error
    if not body:
        raise ValueError(f"VS Code version '{version}' not found for {platform_name}.")
    data = json.loads(body)
    return Build(quality, data["productVersion"], data["url"], data["sha256hash"])


def _extract(archive: Path, target: Path) -> Path:
    """Extract a build archive and return the folder that holds the build."""
    if archive.name.endswith(".tar.gz"):
        extract_tar(archive, target)
    else:
        extract_zip(archive, target)
    entries = list(target.iterdir())
    # The Linux archive wraps the build in one folder (VSCode-linux-x64); a macOS .app is the build.
    if len(entries) == 1 and entries[0].is_dir() and entries[0].suffix != ".app":
        return entries[0]
    return target


def _cache_folder(cache_dir: Path, quality: str, version: str, platform_name: str) -> Path:
    return cache_dir / f"{quality}-{version}-{platform_name}"


# Builds that ``stable`` and ``insiders`` resolved to in this process, by quality and platform.
_latest: dict[tuple[str, str], Build] = {}


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def _newest_cached(cache_dir: Path, quality: str, platform_name: str) -> CachedBuild | None:
    """Return the newest build of ``quality`` in the cache, if there is one."""
    prefix, suffix = f"{quality}-", f"-{platform_name}"
    versions = [
        folder.name[len(prefix) : -len(suffix)] for folder in cache_dir.glob(f"{prefix}*{suffix}") if folder.is_dir()
    ]
    if not versions:
        return None
    version = max(versions, key=_version_key)
    return CachedBuild(_cache_folder(cache_dir, quality, version, platform_name), quality, version)


def _resolve_latest(version: str, platform_name: str, cache_dir: Path) -> Build | CachedBuild:
    """Resolve ``stable`` or ``insiders`` once per process, or use the newest cached build when offline."""
    key = (LATEST[version.lower()], platform_name)
    if key not in _latest:
        try:
            _latest[key] = resolve_build(version, platform_name)
        except OSError:  # the update service cannot be reached
            cached = _newest_cached(cache_dir, key[0], platform_name)
            if cached is None:
                raise
            return cached
    return _latest[key]


def download_vscode(version: str, cache_dir: Path) -> CachedBuild:
    """Return the cached build of ``version``, downloading it first if needed.

    A fixed version that is already cached is returned without network access. ``stable``
    and ``insiders`` are looked up once per process, and offline the newest cached build
    of that quality is used.
    """
    platform_name = vscode_platform()
    if version.lower() in LATEST:
        resolved = _resolve_latest(version, platform_name, cache_dir)
        if isinstance(resolved, CachedBuild):
            return resolved
        build = resolved
    else:
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
        download(build.url, archive)
        actual = sha256(archive)
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


def _application_name(executable: Path, system: str) -> str | None:
    """Return the ``applicationName`` from the build's ``product.json``, such as ``codium`` for VSCodium."""
    product = _app_folder(executable, system) / "product.json"
    try:
        return str(json.loads(product.read_text(encoding="utf-8"))["applicationName"])
    except (OSError, ValueError, KeyError):
        return None


def installed_executable(executable: Path) -> Path:
    """Return the file that ``executable`` names, also as a command on ``PATH`` or through symbolic links."""
    found = shutil.which(str(executable))
    if found is None:
        raise ValueError(f"VS Code executable '{executable}' not found.")
    return Path(found).resolve()


def cli_path(executable: Path, system: str = sys.platform) -> Path:
    """Return the command-line script that belongs to ``executable``, also for forks of VS Code."""
    bin_dir = _app_folder(executable, system) / "bin" if system == "darwin" else executable.parent / "bin"
    suffix = ".cmd" if system == "win32" else ""
    names = dict.fromkeys(name for name in (_application_name(executable, system), "code", "code-insiders") if name)
    for name in names:
        if (bin_dir / f"{name}{suffix}").is_file():
            return bin_dir / f"{name}{suffix}"
    raise ValueError(f"No VS Code command-line script found in {bin_dir}.")


def product_version(executable: Path, system: str = sys.platform) -> str | None:
    """Return the version of the VS Code that ``executable`` belongs to, if it can be found."""
    package = _app_folder(executable, system) / "package.json"
    try:
        return str(json.loads(package.read_text(encoding="utf-8"))["version"])
    except (OSError, ValueError, KeyError):
        return None
