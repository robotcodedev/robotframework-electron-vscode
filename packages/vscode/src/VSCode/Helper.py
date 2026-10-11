"""Helper library for VS Code tests: provide VS Code executables and run VS Code's command line."""

import os
from pathlib import Path

from robot.api.deco import keyword, library

from . import __version__
from .download import cli_path, default_cache_dir, download_vscode, executable_path, select_build
from .instance import instance_environment, run_cli


@library(scope="GLOBAL", version=__version__)
class Helper:
    """Helper keywords for VS Code tests that need no running VS Code.

    `Get VS Code Executable` provides a VS Code executable: a build downloaded
    from the VS Code update service and cached, or a given local one. Use it,
    for example, in a CI setup step that downloads VS Code before the tests
    run. `Execute VS Code CLI Command` runs VS Code's command-line script, for
    example to install extensions into a directory that ``Open VS Code`` uses
    later. The library holds no browser state, so it can be imported next to
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

        *Returns:*
          The path of the VS Code executable.

        *Raises:*
          - ``ValueError``: VS Code has no builds for the current platform, the
                version does not exist for it, or the download does not match
                its checksum.

        Example:
        | ${code} =    `Get VS Code Executable`
        | ${code} =    `Get VS Code Executable`    1.141.0    cache_dir=${EXECDIR}/.cache
        | ${code} =    `Get VS Code Executable`    ${VSCODE_VERSION}    ${VSCODE_EXECUTABLE}
        """
        if executable:
            return str(executable)
        cached = download_vscode(version, cache_dir or default_cache_dir())
        return str(executable_path(cached.folder, cached.quality))

    @keyword("Execute VS Code CLI Command")
    def execute_vs_code_cli_command(
        self,
        extensions_dir: Path,
        user_data_dir: Path,
        *args: str,
        version: str = "stable",
        executable: Path | None = None,
        cache_dir: Path | None = None,
    ) -> str:
        """Runs VS Code's command-line script with ``args`` on the given directories and returns its output.

        The script works on ``extensions_dir`` and ``user_data_dir`` only.
        Both are required, so that a call never changes the user's own
        VS Code. The variables that tie a process to a running VS Code, such
        as those of VS Code's integrated terminal, are removed from the
        script's environment. Use it to install, uninstall, list or update
        extensions, see ``code --help`` for all arguments.

        A running VS Code may not notice what the script changes in its
        extensions directory. The guide on extensions shows how to wait until
        it does.

        *Arguments:*
          - ``extensions_dir``: The extensions directory the script works on.
                A relative path is relative to the working directory of the
                test run.
          - ``user_data_dir``: The user-data directory the script works on,
                relative as ``extensions_dir``.
          - ``args``: The arguments of the script, without
                ``--extensions-dir`` and ``--user-data-dir``.
          - ``version``: The VS Code whose script runs, as for
                `Get VS Code Executable`. Use the VS Code that later opens the
                directories.
          - ``executable``: A VS Code executable to use instead, as for
                `Get VS Code Executable`.
          - ``cache_dir``: Directory for downloaded builds, as for
                `Get VS Code Executable`.

        *Returns:*
          The standard output of the script.

        *Raises:*
          - ``ValueError``: ``args`` contain ``--extensions-dir`` or
                ``--user-data-dir``, or the VS Code is not found.
          - ``RuntimeError``: The script ends with an error or does not finish
                within 10 minutes.

        Example:
        | `Execute VS Code CLI Command`    ${CACHE}/ext    ${CACHE}/data    --install-extension    ms-python.python
        | ${list} =    `Execute VS Code CLI Command`    ${dirs.extensions}    ${dirs.user_data}    --list-extensions
        """
        build = select_build(version, executable, cache_dir)
        return run_cli(
            cli_path(build.executable), extensions_dir, user_data_dir, args, instance_environment(os.environ)
        )
