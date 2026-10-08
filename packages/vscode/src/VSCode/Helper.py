"""Helper library for VS Code tests: provide VS Code executables."""

from pathlib import Path

from robot.api.deco import keyword, library

from . import __version__
from .download import default_cache_dir, download_vscode, executable_path


@library(scope="GLOBAL", version=__version__)
class Helper:
    """Helper keywords for VS Code tests that need no running VS Code.

    `Get VS Code Executable` provides a VS Code executable: a build downloaded
    from the VS Code update service and cached, or a given local one. Use it,
    for example, in a CI setup step that downloads VS Code before the tests
    run. The library holds no browser state, so it can be imported next to
    ``VSCode`` or on its own.

    Example:
    | ***** Settings *****
    | Library    OperatingSystem
    | Library    VSCode.Helper
    |
    | ***** Test Cases *****
    | VS Code Is Available
    |     ${code} =    `Get VS Code Executable`    1.141.0
    |     File Should Exist    ${code}
    """

    @keyword("Get VS Code Executable")
    def get_vs_code_executable(
        self,
        version: str = "stable",
        executable: Path | None = None,
        cache_dir: Path | None = None,
    ) -> str:
        """Returns the VS Code executable of ``version``, downloading it on first use.

        The build for the current platform comes from the VS Code update
        service, is verified against its published SHA-256 checksum and is
        kept in the cache. Later calls, also in later runs, use the cached
        copy. A fixed version that is already cached needs no network access;
        ``stable`` and ``insiders`` always ask the update service for the
        newest build.

        *Arguments:*
          - ``version``: ``stable``, ``insiders`` or a version such as ``1.141.0``.
          - ``executable``: A VS Code executable to use instead, for example an
                installed VS Code or a fork. If given, it is returned unchanged
                and nothing is downloaded. This lets a suite take a local
                VS Code from a variable.
          - ``cache_dir``: Directory for downloaded builds. Defaults to
                ``robotframework-vscode/vscode`` in the user's cache directory
                (``~/.cache`` on Linux, ``~/Library/Caches`` on macOS,
                ``%LOCALAPPDATA%`` on Windows).

        Example:
        | ${code} =    `Get VS Code Executable`
        | ${code} =    `Get VS Code Executable`    1.141.0    cache_dir=${EXECDIR}/.cache
        | ${code} =    `Get VS Code Executable`    ${VSCODE_VERSION}    ${VSCODE_EXECUTABLE}
        """
        if executable:
            return str(executable)
        cached = download_vscode(version, cache_dir or default_cache_dir())
        return str(executable_path(cached.folder, cached.quality))
