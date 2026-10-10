"""Helper library for Electron tests: download Electron releases."""

import hashlib
import os
import platform
import shutil
import stat
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from robot.api.deco import keyword, library

from . import __version__

RELEASES_URL = "https://github.com/electron/electron/releases/download"

# Seconds that a network operation, such as connecting or receiving the next data, may take.
NETWORK_TIMEOUT = 60


def architecture(machine: str, product: str) -> str:
    """Return ``x64`` or ``arm64`` for ``machine``, or fail for other processor architectures."""
    name = machine.lower()
    if name in ("x86_64", "amd64"):
        return "x64"
    if name in ("arm64", "aarch64"):
        return "arm64"
    raise ValueError(f"{product} is not available for the processor architecture '{machine}'.")


def electron_platform(system: str = sys.platform, machine: str = platform.machine()) -> str:
    """Return the platform part of Electron's release asset names, for example ``linux-x64``."""
    names = {"linux": "linux", "win32": "win32", "darwin": "darwin"}
    if system not in names:
        raise ValueError(f"Electron releases are not available for platform '{system}'.")
    return f"{names[system]}-{architecture(machine, 'Electron')}"


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


def open_url(url: str) -> Any:
    """Open ``url``, failing when a network operation takes longer than ``NETWORK_TIMEOUT``."""
    return urllib.request.urlopen(url, timeout=NETWORK_TIMEOUT)


def download(url: str, target: Path) -> None:
    """Download ``url`` into the file ``target``."""
    try:
        with open_url(url) as response, open(target, "wb") as file:
            shutil.copyfileobj(response, file)
    except TimeoutError as error:
        raise TimeoutError(f"Downloading {url} timed out: no data for {NETWORK_TIMEOUT} seconds.") from error


def sha256(path: Path) -> str:
    """Return the SHA-256 checksum of a file, reading it in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(root: Path, path: Path, name: str) -> Path:
    """Return ``path`` resolved, or fail if it is not inside ``root``."""
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Archive entry '{name}' points outside the folder it is extracted to.")
    return resolved


def extract_zip(archive: Path, target: Path) -> None:
    """Extract a zip and keep file modes and symlinks, which zipfile drops.

    Every entry and every symlink target must stay inside ``target``. Symlinks are
    created after all files, so that no file is written through one.
    """
    target.mkdir(parents=True, exist_ok=True)
    root = target.resolve()
    links: list[tuple[Path, str]] = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            path = _inside(root, target / info.filename, info.filename)
            mode = info.external_attr >> 16
            if info.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            elif stat.S_ISLNK(mode):
                links.append((path, zf.read(info).decode()))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                if mode:
                    path.chmod(stat.S_IMODE(mode))
    for path, link in links:
        _inside(root, path.parent / link, f"{path.relative_to(root)} -> {link}")
        path.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(link, path)


def extract_tar(archive: Path, target: Path) -> None:
    """Extract a tar archive whose entries and links all stay inside ``target``."""
    target.mkdir(parents=True, exist_ok=True)
    root = target.resolve()
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            path = _inside(root, target / member.name, member.name)
            if member.issym():
                _inside(root, path.parent / member.linkname, f"{member.name} -> {member.linkname}")
            elif member.islnk():
                _inside(root, target / member.linkname, f"{member.name} -> {member.linkname}")
            elif not (member.isfile() or member.isdir()):
                raise ValueError(f"Archive entry '{member.name}' is neither a file, a folder nor a link.")
        if hasattr(tarfile, "tar_filter"):
            tar.extractall(target, members=members, filter="tar")
        else:  # Python < 3.12 has no extraction filters; the checks above cover them.
            tar.extractall(target, members=members)


def _expected_sha256(release_url: str, asset: str, version: str) -> str:
    try:
        with open_url(f"{release_url}/SHASUMS256.txt") as response:
            lines: list[str] = response.read().decode().splitlines()
    except urllib.error.HTTPError as error:
        raise ValueError(f"Electron release '{version}' not found ({error.code} for {release_url}).") from error
    for line in lines:
        checksum, _, name = line.partition(" ")
        if name.strip().lstrip("*") == asset:
            return checksum
    raise ValueError(f"Electron release '{version}' has no download '{asset}'.")


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
        download(f"{release_url}/{asset}", archive)
        actual = sha256(archive)
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
