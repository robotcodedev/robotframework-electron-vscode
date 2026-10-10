"""Helper library for Electron tests: download Electron releases."""

import hashlib
import os
import platform
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from robot.api.deco import keyword, library

from . import __version__

RELEASES_URL = "https://github.com/electron/electron/releases/download"


def electron_platform(system: str = sys.platform, machine: str = platform.machine()) -> str:
    """Return the platform part of Electron's release asset names, for example ``linux-x64``."""
    names = {"linux": "linux", "win32": "win32", "darwin": "darwin"}
    if system not in names:
        raise ValueError(f"Electron releases are not available for platform '{system}'.")
    arch = "arm64" if machine.lower() in ("arm64", "aarch64") else "x64"
    return f"{names[system]}-{arch}"


def executable_path(folder: Path, system: str = sys.platform) -> Path:
    """Return the Electron executable inside an extracted release folder."""
    if system == "win32":
        return folder / "electron.exe"
    if system == "darwin":
        return folder / "Electron.app" / "Contents" / "MacOS" / "Electron"
    return folder / "electron"


def user_cache_dir() -> Path:
    """Return the platform's cache directory for the current user."""
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches"
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))


def default_cache_dir() -> Path:
    """Return the user's cache directory for Electron releases."""
    return user_cache_dir() / "robotframework-electron" / "electron"


def _open(url: str):
    return urllib.request.urlopen(url)


def _expected_sha256(release_url: str, asset: str, version: str) -> str:
    try:
        with _open(f"{release_url}/SHASUMS256.txt") as response:
            lines = response.read().decode().splitlines()
    except urllib.error.HTTPError as error:
        raise ValueError(f"Electron release '{version}' not found ({error.code} for {release_url}).") from error
    for line in lines:
        checksum, _, name = line.partition(" ")
        if name.strip().lstrip("*") == asset:
            return checksum
    raise ValueError(f"Electron release '{version}' has no download '{asset}'.")


def extract_zip(archive: Path, target: Path) -> None:
    """Extract a zip and keep file modes and symlinks, which zipfile drops."""
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            path = target / info.filename
            mode = info.external_attr >> 16
            if info.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            elif stat.S_ISLNK(mode):
                path.parent.mkdir(parents=True, exist_ok=True)
                os.symlink(zf.read(info).decode(), path)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                if mode:
                    path.chmod(stat.S_IMODE(mode))


def download_electron(version: str, cache_dir: Path) -> Path:
    """Return the cached release folder of ``version``, downloading it first if needed."""
    version = version.removeprefix("v")
    name = f"v{version}-{electron_platform()}"
    folder = cache_dir / name
    if folder.is_dir():
        return folder
    release_url = f"{RELEASES_URL}/v{version}"
    asset = f"electron-{name}.zip"
    expected = _expected_sha256(release_url, asset, version)
    cache_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache_dir) as tmp:
        archive = Path(tmp, asset)
        with _open(f"{release_url}/{asset}") as response, open(archive, "wb") as file:
            shutil.copyfileobj(response, file)
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Checksum mismatch for {asset}: got {actual}, expected {expected}.")
        extracted = Path(tmp, "extracted")
        extract_zip(archive, extracted)
        try:
            os.replace(extracted, folder)
        except OSError:
            if not folder.is_dir():  # another process may have won the race
                raise
    return folder


@library(scope="GLOBAL", version=__version__)
class Helper:
    """Helper keywords for Electron tests that need no running application.

    `Get Electron Executable` provides an Electron binary of a given version,
    for example to start an app from its source folder with the plain
    Electron binary. The library holds no browser state, so it can be
    imported next to ``Electron`` or on its own.

    Example:
    | ***** Settings *****
    | Library    Electron
    | Library    Electron.Helper
    |
    | ***** Test Cases *****
    | App From Source
    |     ${electron} =    `Get Electron Executable`    44.7.0
    |     New Electron Application    ${electron}    args=${{ [$EXECDIR + "/app"] }}
    """

    @keyword
    def get_electron_executable(
        self,
        version: str,
        executable: Path | None = None,
        cache_dir: Path | None = None,
    ) -> str:
        """Returns the Electron executable of ``version``, downloading it on first use.

        The release is downloaded from GitHub for the current platform,
        verified against its published SHA-256 checksum and kept in the cache.
        Later calls, also in later runs, use the cached copy.

        *Arguments:*
          - ``version``: Electron version, for example ``44.7.0``.
          - ``executable``: An Electron executable to use instead. If given,
                it is returned unchanged and nothing is downloaded. This lets a
                suite take a locally installed Electron from a variable.
          - ``cache_dir``: Directory for downloaded releases. Defaults to
                ``robotframework-electron/electron`` in the user's cache
                directory (``~/.cache`` on Linux, ``~/Library/Caches`` on
                macOS, ``%LOCALAPPDATA%`` on Windows).

        *Returns:*
          The path of the Electron executable.

        *Raises:*
          - ``ValueError``: Electron has no releases for the current platform,
                the version does not exist or has no download for the
                platform, or the download does not match its checksum.

        Example:
        | ${electron} =    `Get Electron Executable`    44.7.0
        | ${electron} =    `Get Electron Executable`    ${ELECTRON_VERSION}    ${ELECTRON_EXECUTABLE}
        """
        if executable:
            return str(executable)
        folder = download_electron(version, cache_dir or default_cache_dir())
        return str(executable_path(folder))
