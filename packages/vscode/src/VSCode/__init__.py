"""Robot Framework library for end-to-end testing of VS Code extensions."""

import os
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any, NamedTuple

from Browser.utils import logger
from Browser.utils.data_types import ElementState, NewPageDetails, SelectionType
from Electron import Electron
from robotlibcore import keyword

from .download import cli_path, default_cache_dir, download_vscode, executable_path, product_version
from .instance import (
    create_instance_directories,
    install_extension,
    instance_environment,
    launch_arguments,
    write_settings,
)

__version__ = version("robotframework-vscode")

_INTRO = """
VSCode library is a Robot Framework library for end-to-end testing of VS Code extensions.

It is built on the Electron library, which is built on the
[https://robotframework-browser.org|Browser library]: it contains every
Electron and Browser keyword and takes Browser's import arguments. Import
``VSCode`` instead of ``Browser`` or ``Electron``.

`Open VS Code` downloads VS Code if needed and starts an isolated instance
with the extension under test, `Close VS Code` ends it. The workbench
window is an ordinary Browser page. `Download VS Code` provides a VS Code
executable on its own, for example in a CI setup step.

= Electron library documentation =

The rest of this documentation is the Electron library's own.
"""


class VSCodeInstance(NamedTuple):
    directory: Path
    version: str | None


class VSCode(Electron):
    ROBOT_LIBRARY_VERSION = __version__

    def _vscode_instances(self) -> dict[str, VSCodeInstance]:
        return self.__dict__.setdefault("_vscode_instance_registry", {})

    @keyword("Download VS Code")
    def download_vs_code(self, version: str = "stable", cache_dir: Path | None = None) -> str:
        """Downloads VS Code and returns the path of its executable.

        The build for the current platform comes from the VS Code update
        service, is verified against its published SHA-256 checksum and is
        kept in the cache. Later calls, also in later runs, use the cached
        copy. A fixed version that is already cached needs no network access;
        ``stable`` and ``insiders`` always ask the update service for the
        newest build.

        *Arguments:*
          - ``version``: ``stable``, ``insiders`` or a version such as ``1.141.0``.
          - ``cache_dir``: Directory for downloaded builds. Defaults to
                ``robotframework-vscode/vscode`` in the user's cache directory
                (``~/.cache`` on Linux, ``~/Library/Caches`` on macOS,
                ``%LOCALAPPDATA%`` on Windows).

        Example:
        | ${code} =    `Download VS Code`
        | ${code} =    `Download VS Code`    1.141.0    cache_dir=${EXECDIR}/.cache
        """
        cached = download_vscode(version, cache_dir or default_cache_dir())
        return str(executable_path(cached.folder, cached.quality))

    @keyword("Open VS Code")
    def open_vs_code(
        self,
        path: Path | None = None,
        *,
        version: str = "stable",
        executable: Path | None = None,
        extension_development_path: Path | list[Path] | None = None,
        extensions: list[str] | None = None,
        settings: dict[str, Any] | None = None,
        args: list[str] | None = None,
        cache_dir: Path | None = None,
        timeout: timedelta = timedelta(seconds=60),
    ) -> tuple[str, str, NewPageDetails]:
        """Starts an isolated VS Code instance and returns once its workbench is ready.

        Each instance gets its own user-data and extensions directories in
        ``vscode/<n>`` under the output directory, so neither the user's own
        VS Code nor other instances affect it. The directories are kept after
        the instance ends, with VS Code's logs in ``user-data/logs``.
        Variables that tie a process to a running VS Code (``VSCODE_*`` and
        ``ELECTRON_RUN_AS_NODE``) are removed from the instance's environment.

        The instance is an application as started by `New Electron
        Application`: its workbench window is the active page, Browser
        keywords work on it, and `Close VS Code`, `Close Browser` and
        automatic closing end it.

        *Arguments:*
          - ``path``: A folder to open as workspace, or a file to open in an editor.
          - ``version``: VS Code to download and start, as for `Download VS Code`:
                ``stable``, ``insiders`` or a version such as ``1.141.0``.
          - ``executable``: An installed VS Code executable to start instead.
                Nothing is downloaded then.
          - ``extension_development_path``: Folder of the extension under test,
                or a list of folders. They are loaded as development extensions.
          - ``extensions``: Extensions to install into the instance before it
                starts, as Marketplace identifiers or ``.vsix`` files.
          - ``settings``: User settings for the instance. They override the
                defaults, which switch off the welcome page, update checks,
                telemetry, workspace trust, the screen reader mode and the
                secondary side bar.
          - ``args``: Additional command-line arguments for VS Code.
          - ``cache_dir``: Cache directory for downloads, see `Download VS Code`.
          - ``timeout``: How long to wait for the window and for the workbench.

        Returns a tuple of browser id, context id and page details of the
        workbench window, like `New Electron Application`.

        Example:
        | `Open VS Code`    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
        | `Open VS Code`    version=1.141.0    settings=${{ {"window.title": "robot-test"} }}
        """
        if executable is None:
            cached = download_vscode(version, cache_dir or default_cache_dir())
            executable = executable_path(cached.folder, cached.quality)
            product = cached.version
        else:
            product = product_version(Path(executable))
        directories = create_instance_directories(Path(self.outputdir))
        write_settings(directories.user_data, settings)
        env = instance_environment(os.environ)
        for extension in extensions or []:
            install_extension(cli_path(Path(executable)), extension, directories, env)
        if isinstance(extension_development_path, Path):
            extension_development_path = [extension_development_path]
        arguments = launch_arguments(directories, extension_development_path or [], args or [], path)
        logger.info(f"Starting VS Code {product or executable} with instance directory {directories.root}")
        ids = self.new_electron_application(executable, args=arguments, env=env, timeout=timeout)
        try:
            self.wait_for_elements_state(".monaco-workbench", ElementState.visible, timeout)
        except Exception:
            self.close_browser(ids[0])
            raise
        self._vscode_instances()[ids[0]] = VSCodeInstance(directories.root, product)
        return ids

    @keyword("Close VS Code")
    def close_vs_code(self, browser: SelectionType | str = SelectionType.CURRENT) -> None:
        """Ends a VS Code instance started with `Open VS Code`.

        The keyword returns after the VS Code process has exited. It behaves
        like `Close Electron Application`: ``CURRENT`` ends the active
        instance, a browser id ends that instance, ``ALL`` closes all
        browsers and applications.

        Example:
        | ${vscode}    ${_}    ${_} =    `Open VS Code`
        | `Close VS Code`    ${vscode}
        """
        self.close_electron_application(browser)


VSCode.__doc__ = cleandoc(_INTRO) + "\n\n" + cleandoc(Electron.__doc__ or "")

__all__ = ["VSCode"]
