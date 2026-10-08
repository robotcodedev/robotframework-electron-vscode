import hashlib
import io
import os
import stat
import sys
import urllib.error
import zipfile
from pathlib import Path

import pytest

from Electron import Helper as helper_module
from Electron.Helper import (
    Helper,
    download_electron,
    electron_platform,
    executable_path,
)

VERSION = "1.2.3"


def make_release_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        info = zipfile.ZipInfo(executable_path(Path()).as_posix())
        info.external_attr = (stat.S_IFREG | 0o755) << 16
        zf.writestr(info, "#!/bin/sh\n")
    return buffer.getvalue()


class FakeReleases:
    def __init__(self, checksum: str | None = None):
        self.archive = make_release_zip()
        self.asset = f"electron-v{VERSION}-{electron_platform()}.zip"
        digest = checksum or hashlib.sha256(self.archive).hexdigest()
        self.files = {
            f"v{VERSION}/SHASUMS256.txt": f"{digest} *{self.asset}\n".encode(),
            f"v{VERSION}/{self.asset}": self.archive,
        }
        self.requests: list[str] = []

    def open(self, url: str):
        self.requests.append(url)
        key = url.removeprefix(helper_module.RELEASES_URL + "/")
        if key not in self.files:
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        return io.BytesIO(self.files[key])


@pytest.fixture
def releases(monkeypatch):
    fake = FakeReleases()
    monkeypatch.setattr(helper_module, "_open", fake.open)
    return fake


@pytest.mark.parametrize(
    ("system", "machine", "expected"),
    [
        ("linux", "x86_64", "linux-x64"),
        ("linux", "aarch64", "linux-arm64"),
        ("darwin", "arm64", "darwin-arm64"),
        ("darwin", "x86_64", "darwin-x64"),
        ("win32", "AMD64", "win32-x64"),
    ],
)
def test_maps_platform_to_release_asset_names(system, machine, expected):
    assert electron_platform(system, machine) == expected


def test_rejects_unsupported_platform():
    with pytest.raises(ValueError, match="freebsd"):
        electron_platform("freebsd", "x86_64")


@pytest.mark.parametrize(
    ("system", "expected"),
    [
        ("linux", "electron"),
        ("win32", "electron.exe"),
        ("darwin", "Electron.app/Contents/MacOS/Electron"),
    ],
)
def test_finds_executable_in_release_folder(system, expected):
    assert executable_path(Path("release"), system) == Path("release", expected)


def test_downloads_once_and_then_uses_the_cache(releases, tmp_path):
    first = Helper().get_electron_executable(VERSION, cache_dir=tmp_path)
    downloads = len(releases.requests)
    second = Helper().get_electron_executable(VERSION, cache_dir=tmp_path)

    assert first == second
    assert len(releases.requests) == downloads
    assert Path(first).is_file()


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")
def test_keeps_the_executable_bit(releases, tmp_path):
    executable = Helper().get_electron_executable(VERSION, cache_dir=tmp_path)

    assert os.access(executable, os.X_OK)


def test_checksum_mismatch_fails_and_leaves_nothing_in_the_cache(monkeypatch, tmp_path):
    fake = FakeReleases(checksum="0" * 64)
    monkeypatch.setattr(helper_module, "_open", fake.open)

    with pytest.raises(ValueError, match="Checksum mismatch"):
        download_electron(VERSION, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_unknown_version_names_the_version(releases, tmp_path):
    with pytest.raises(ValueError, match="'0.0.1' not found"):
        download_electron("0.0.1", tmp_path)


def test_returns_given_executable_without_downloading(releases, tmp_path):
    executable = Helper().get_electron_executable(VERSION, executable=Path("/opt/electron/electron"), cache_dir=tmp_path)

    assert executable == str(Path("/opt/electron/electron"))
    assert releases.requests == []
