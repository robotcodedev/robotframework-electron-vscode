import hashlib
import io
import json
import os
import stat
import sys
import tarfile
import threading
import urllib.error
from email.message import Message
from pathlib import Path

import pytest

import Electron.Helper
from VSCode import download
from VSCode.download import (
    UPDATE_SERVICE,
    cli_path,
    download_vscode,
    executable_path,
    installed_executable,
    product_version,
    resolve_build,
    select_build,
    vscode_platform,
)

PLATFORM = vscode_platform()


def make_linux_archive(version: str) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, content, mode in [
            ("VSCode-linux-x64/code", b"#!/bin/sh\n", 0o755),
            ("VSCode-linux-x64/bin/code", b"#!/bin/sh\n", 0o755),
            ("VSCode-linux-x64/resources/app/package.json", json.dumps({"version": version}).encode(), 0o644),
        ]:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            info.mode = mode
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


class FakeUpdateService:
    def __init__(self, checksum: str | None = None, broken_download: bool = False):
        self.archive = make_linux_archive("1.2.3")
        self.checksum = checksum or hashlib.sha256(self.archive).hexdigest()
        self.broken_download = broken_download
        self.requests: list[str] = []
        self._lock = threading.Lock()

    def build(self, version: str, quality: str) -> bytes:
        return json.dumps(
            {
                "productVersion": version,
                "url": f"https://download.example/{quality}/{version}/code.tar.gz",
                "sha256hash": self.checksum,
            }
        ).encode()

    def open(self, url: str):
        with self._lock:
            self.requests.append(url)
        answers = {
            f"{UPDATE_SERVICE}/api/update/{PLATFORM}/stable/latest": self.build("1.2.3", "stable"),
            f"{UPDATE_SERVICE}/api/update/{PLATFORM}/insider/latest": self.build("1.3.0-insider", "insider"),
            f"{UPDATE_SERVICE}/api/versions/1.2.3/{PLATFORM}/stable": self.build("1.2.3", "stable"),
        }
        if url in answers:
            return io.BytesIO(answers[url])
        if url.startswith("https://download.example/"):
            if self.broken_download:
                return BrokenStream()
            return io.BytesIO(self.archive)
        raise urllib.error.HTTPError(url, 404, "Not Found", Message(), None)


class BrokenStream(io.BytesIO):
    def read(self, *args):
        raise ConnectionResetError("connection lost")


@pytest.fixture(autouse=True)
def _fresh_latest_builds(monkeypatch):
    # `stable` and `insiders` are resolved once per process; every test starts without them.
    monkeypatch.setattr(download, "_latest", {})


@pytest.fixture
def service(monkeypatch):
    fake = FakeUpdateService()
    monkeypatch.setattr(Electron.Helper, "open_url", fake.open)
    return fake


@pytest.mark.parametrize(
    ("system", "machine", "expected"),
    [
        ("linux", "x86_64", "linux-x64"),
        ("linux", "aarch64", "linux-arm64"),
        ("win32", "AMD64", "win32-x64-archive"),
        ("darwin", "arm64", "darwin-arm64"),
        ("darwin", "x86_64", "darwin"),
    ],
)
def test_maps_platform_to_update_service_names(system, machine, expected):
    assert vscode_platform(system, machine) == expected


def test_resolves_newest_stable_build(service):
    build = resolve_build("stable", PLATFORM)

    assert (build.quality, build.version) == ("stable", "1.2.3")


@pytest.mark.parametrize("version", ["insiders", "insider"])
def test_resolves_newest_insiders_build(service, version):
    build = resolve_build(version, PLATFORM)

    assert (build.quality, build.version) == ("insider", "1.3.0-insider")


def test_resolves_fixed_version(service):
    assert resolve_build("1.2.3", PLATFORM).version == "1.2.3"


def test_unknown_version_names_the_version(service):
    with pytest.raises(ValueError, match=r"'0\.0\.1' not found"):
        resolve_build("0.0.1", PLATFORM)


@pytest.mark.skipif(sys.platform != "linux", reason="fake archive has the Linux layout")
def test_downloads_once_and_then_uses_the_cache(service, tmp_path):
    first = download_vscode("stable", tmp_path).folder
    downloads = [url for url in service.requests if url.startswith("https://download.example/")]
    second = download_vscode("stable", tmp_path).folder

    assert first == second == tmp_path / f"stable-1.2.3-{PLATFORM}"
    assert [url for url in service.requests if url.startswith("https://download.example/")] == downloads
    assert os.access(executable_path(first, "stable"), os.X_OK)


@pytest.mark.skipif(sys.platform != "linux", reason="fake archive has the Linux layout")
def test_cached_fixed_version_needs_no_network(service, tmp_path):
    download_vscode("1.2.3", tmp_path)
    service.requests.clear()

    cached = download_vscode("1.2.3", tmp_path)

    assert service.requests == []
    assert cached == (tmp_path / f"stable-1.2.3-{PLATFORM}", "stable", "1.2.3")


def test_checksum_mismatch_fails_and_leaves_nothing_in_the_cache(monkeypatch, tmp_path):
    fake = FakeUpdateService(checksum="0" * 64)
    monkeypatch.setattr(Electron.Helper, "open_url", fake.open)

    with pytest.raises(ValueError, match="Checksum mismatch"):
        download_vscode("stable", tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_interrupted_download_leaves_nothing_in_the_cache(monkeypatch, tmp_path):
    fake = FakeUpdateService(broken_download=True)
    monkeypatch.setattr(Electron.Helper, "open_url", fake.open)

    with pytest.raises(ConnectionResetError):
        download_vscode("stable", tmp_path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.skipif(sys.platform != "linux", reason="fake archive has the Linux layout")
def test_concurrent_downloads_end_with_one_build_and_the_same_path(service, tmp_path):
    results: list[Path] = []

    def fetch():
        results.append(download_vscode("stable", tmp_path).folder)

    threads = [threading.Thread(target=fetch) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results[0] == results[1]
    assert [path.name for path in tmp_path.iterdir()] == [f"stable-1.2.3-{PLATFORM}"]


@pytest.mark.parametrize(
    ("system", "quality", "expected"),
    [
        ("linux", "stable", "code"),
        ("linux", "insider", "code-insiders"),
        ("win32", "stable", "Code.exe"),
        ("win32", "insider", "Code - Insiders.exe"),
    ],
)
def test_finds_executable_in_build_folder(system, quality, expected):
    assert executable_path(Path("build"), quality, system) == Path("build", expected)


def test_finds_executable_in_macos_app_bundle(tmp_path):
    binary = tmp_path / "Visual Studio Code.app" / "Contents" / "MacOS" / "Code"
    binary.parent.mkdir(parents=True)
    binary.touch()

    assert executable_path(tmp_path, "stable", "darwin") == binary


@pytest.mark.parametrize(
    ("system", "executable", "cli"),
    [
        ("linux", "code", "bin/code"),
        ("linux", "code-insiders", "bin/code-insiders"),
        ("win32", "Code.exe", "bin/code.cmd"),
        (
            "darwin",
            "Visual Studio Code.app/Contents/MacOS/Code",
            "Visual Studio Code.app/Contents/Resources/app/bin/code",
        ),
    ],
)
def test_finds_command_line_script_next_to_executable(tmp_path, system, executable, cli):
    (tmp_path / cli).parent.mkdir(parents=True)
    (tmp_path / cli).touch()

    assert cli_path(tmp_path / executable, system) == tmp_path / cli


def test_reads_product_version_of_an_installation(tmp_path):
    package = tmp_path / "resources" / "app" / "package.json"
    package.parent.mkdir(parents=True)
    package.write_text(json.dumps({"version": "1.141.0"}))

    assert product_version(tmp_path / "code", "linux") == "1.141.0"
    assert product_version(tmp_path / "missing" / "code", "linux") is None


def test_extracted_files_keep_their_mode(service, tmp_path):
    if sys.platform != "linux":
        pytest.skip("fake archive has the Linux layout")
    folder = download_vscode("stable", tmp_path).folder

    assert stat.S_IMODE((folder / "bin" / "code").stat().st_mode) & 0o111


@pytest.mark.parametrize(
    ("system", "executable", "application_name", "cli"),
    [
        ("linux", "code", "code", "bin/code"),
        ("linux", "code-insiders", "code-insiders", "bin/code-insiders"),
        ("linux", "codium", "codium", "bin/codium"),
        ("linux", "cursor", "cursor", "bin/cursor"),
        ("win32", "VSCodium.exe", "codium", "bin/codium.cmd"),
        ("darwin", "VSCodium.app/Contents/MacOS/Electron", "codium", "VSCodium.app/Contents/Resources/app/bin/codium"),
    ],
)
def test_finds_command_line_script_by_product_application_name(tmp_path, system, executable, application_name, cli):
    app_folder = (
        tmp_path / "VSCodium.app" / "Contents" / "Resources" / "app"
        if system == "darwin"
        else tmp_path / "resources" / "app"
    )
    app_folder.mkdir(parents=True)
    (app_folder / "product.json").write_text(json.dumps({"applicationName": application_name}))
    (tmp_path / cli).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / cli).touch()

    assert cli_path(tmp_path / executable, system) == tmp_path / cli


def test_reports_missing_command_line_script(tmp_path):
    with pytest.raises(ValueError, match="No VS Code command-line script found"):
        cli_path(tmp_path / "codium", "linux")


def test_rejects_unsupported_architecture():
    with pytest.raises(ValueError, match="armv7l"):
        vscode_platform("linux", "armv7l")


@pytest.mark.skipif(sys.platform != "linux", reason="fake archive has the Linux layout")
def test_stable_is_looked_up_once_per_process(service, tmp_path):
    first = download_vscode("stable", tmp_path)
    second = download_vscode("stable", tmp_path)

    assert first == second
    latest = f"{UPDATE_SERVICE}/api/update/{PLATFORM}/stable/latest"
    assert service.requests.count(latest) == 1


def unreachable(url: str):
    raise urllib.error.URLError("no network")


def test_newest_cached_build_is_used_when_the_update_service_is_unreachable(monkeypatch, tmp_path):
    for version in ("1.9.0", "1.10.0", "1.2.3"):
        (tmp_path / f"stable-{version}-{PLATFORM}").mkdir()
    (tmp_path / f"insider-1.11.0-insider-{PLATFORM}").mkdir()
    monkeypatch.setattr(Electron.Helper, "open_url", unreachable)

    cached = download_vscode("stable", tmp_path)

    assert cached.version == "1.10.0"
    assert cached.folder == tmp_path / f"stable-1.10.0-{PLATFORM}"


def test_unreachable_update_service_without_cached_build_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(Electron.Helper, "open_url", unreachable)

    with pytest.raises(urllib.error.URLError):
        download_vscode("stable", tmp_path)


def make_executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("")
    path.chmod(0o755)
    return path


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executables and symbolic links")
def test_given_executable_is_resolved_through_symbolic_links(tmp_path):
    target = make_executable(tmp_path / "VSCode-linux-x64" / "code")
    make_executable(tmp_path / "VSCode-linux-x64" / "bin" / "code")
    link = tmp_path / "links" / "code"
    link.parent.mkdir()
    link.symlink_to(target)

    executable = installed_executable(link)

    assert executable == target.resolve()
    assert cli_path(executable, "linux") == target.resolve().parent / "bin" / "code"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executables")
def test_given_executable_is_found_on_path(tmp_path, monkeypatch):
    target = make_executable(tmp_path / "bin" / "my-code")
    monkeypatch.setenv("PATH", str(target.parent))

    assert installed_executable(Path("my-code")) == target.resolve()


def test_missing_executable_is_reported(tmp_path):
    with pytest.raises(ValueError, match=r"VS Code executable '.*missing-code' not found"):
        installed_executable(tmp_path / "missing-code")


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX executables")
def test_selects_a_given_executable_with_its_version(tmp_path):
    target = make_executable(tmp_path / "VSCode-linux-x64" / "code")
    package = tmp_path / "VSCode-linux-x64" / "resources" / "app" / "package.json"
    package.parent.mkdir(parents=True)
    package.write_text(json.dumps({"version": "1.141.0"}))

    build = select_build("stable", target, None)

    assert build == (target.resolve(), "1.141.0")


@pytest.mark.skipif(sys.platform != "linux", reason="fake archive has the Linux layout")
def test_selects_a_version_from_the_cache(service, tmp_path):
    build = select_build("stable", None, tmp_path)

    assert build == (executable_path(tmp_path / f"stable-1.2.3-{PLATFORM}", "stable"), "1.2.3")
