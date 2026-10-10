import hashlib
import io
import os
import stat
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from email.message import Message
from pathlib import Path

import pytest

from Electron import Helper as HelperModule
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
        key = url.removeprefix(HelperModule.RELEASES_URL + "/")
        if key not in self.files:
            raise urllib.error.HTTPError(url, 404, "Not Found", Message(), None)
        return io.BytesIO(self.files[key])


@pytest.fixture
def releases(monkeypatch):
    fake = FakeReleases()
    monkeypatch.setattr(HelperModule, "open_url", fake.open)
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
    monkeypatch.setattr(HelperModule, "open_url", fake.open)

    with pytest.raises(ValueError, match="Checksum mismatch"):
        download_electron(VERSION, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_unknown_version_names_the_version(releases, tmp_path):
    with pytest.raises(ValueError, match=r"'0\.0\.1' not found"):
        download_electron("0.0.1", tmp_path)


def test_returns_given_executable_without_downloading(releases, tmp_path):
    executable = Helper().get_electron_executable(
        VERSION, executable=Path("/opt/electron/electron"), cache_dir=tmp_path
    )

    assert executable == str(Path("/opt/electron/electron"))
    assert releases.requests == []


def test_rejects_unsupported_architecture():
    with pytest.raises(ValueError, match="armv7l"):
        electron_platform("linux", "armv7l")


def test_network_operations_have_a_timeout(monkeypatch):
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(urllib.request, "urlopen", lambda url, **kwargs: calls.append(kwargs))

    HelperModule.open_url("https://example.org/")

    assert calls == [{"timeout": HelperModule.NETWORK_TIMEOUT}]


class StalledStream(io.BytesIO):
    def read(self, *args):
        raise TimeoutError("timed out")


def test_download_names_the_url_when_the_server_stops_sending(monkeypatch, tmp_path):
    monkeypatch.setattr(HelperModule, "open_url", lambda url: StalledStream())

    with pytest.raises(TimeoutError, match=r"https://example\.org/file\.zip"):
        HelperModule.download("https://example.org/file.zip", tmp_path / "file.zip")


def make_zip(path: Path, entries: list[tuple[str, bytes, int]]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, content, mode in entries:
            info = zipfile.ZipInfo(name)
            info.external_attr = mode << 16
            zf.writestr(info, content)
    return path


@pytest.mark.parametrize("name", ["../evil.txt", "folder/../../evil.txt"])
def test_zip_entry_outside_the_folder_is_refused(tmp_path, name):
    archive = make_zip(tmp_path / "evil.zip", [(name, b"evil", stat.S_IFREG | 0o644)])

    with pytest.raises(ValueError, match="outside"):
        HelperModule.extract_zip(archive, tmp_path / "target")

    assert not (tmp_path / "evil.txt").exists()


def test_zip_symlink_pointing_outside_the_folder_is_refused(tmp_path):
    archive = make_zip(tmp_path / "evil.zip", [("link", b"../../outside", stat.S_IFLNK | 0o777)])

    with pytest.raises(ValueError, match="outside"):
        HelperModule.extract_zip(archive, tmp_path / "target")

    assert not (tmp_path / "target" / "link").is_symlink()


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges on Windows")
def test_zip_symlink_inside_the_folder_is_kept(tmp_path):
    archive = make_zip(
        tmp_path / "app.zip",
        [
            ("app/Versions/A/binary", b"#!/bin/sh\n", stat.S_IFREG | 0o755),
            ("app/Current", b"Versions/A", stat.S_IFLNK | 0o777),
        ],
    )

    HelperModule.extract_zip(archive, tmp_path / "target")

    assert (tmp_path / "target" / "app" / "Current" / "binary").read_text() == "#!/bin/sh\n"


def make_tar(path: Path, members: list[tarfile.TarInfo]) -> Path:
    with tarfile.open(path, "w:gz") as tar:
        for member in members:
            tar.addfile(member, io.BytesIO(b"x" * member.size) if member.isfile() else None)
    return path


def tar_member(name: str, kind: bytes = tarfile.REGTYPE, link: str = "") -> tarfile.TarInfo:
    member = tarfile.TarInfo(name)
    member.type = kind
    member.linkname = link
    member.size = 1 if kind == tarfile.REGTYPE else 0
    return member


@pytest.mark.parametrize(
    "member",
    [
        tar_member("../evil.txt"),
        tar_member("/evil.txt"),
        tar_member("link", tarfile.SYMTYPE, "../../outside"),
        tar_member("hard", tarfile.LNKTYPE, "../outside"),
    ],
    ids=["parent", "absolute", "symlink", "hardlink"],
)
def test_tar_entry_outside_the_folder_is_refused(tmp_path, member):
    archive = make_tar(tmp_path / "evil.tar.gz", [member])

    with pytest.raises(ValueError, match="outside"):
        HelperModule.extract_tar(archive, tmp_path / "target")

    assert not (tmp_path / "evil.txt").exists()
    assert list((tmp_path / "target").iterdir()) == []
