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
    InstanceDirectories,
    create_instance_directories,
    install_extension,
    instance_environment,
    launch_arguments,
    remove_instance_directories,
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
window is an ordinary Browser page. To get a VS Code executable without
starting it, for example in a CI setup step, use ``Get VS Code Executable``
from the ``VSCode.Helper`` library.

= Electron library documentation =

The rest of this documentation is the Electron library's own.
"""


class Instance(NamedTuple):
    executable: Path
    directories: InstanceDirectories


class VSCode(Electron):
    ROBOT_LIBRARY_VERSION = __version__

    _instance_cleanup_done = False

    def _start_suite(self, name, attrs):
        super()._start_suite(name, attrs)
        # Like Browser's output folders: once per process, before the run opens its first instance.
        if not VSCode._instance_cleanup_done:
            VSCode._instance_cleanup_done = True
            remove_instance_directories(Path(self.outputdir))

    def _instances(self) -> dict[str, Instance]:
        return self.__dict__.setdefault("_vscode_instances", {})

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
          - ``version``: VS Code to download and start: ``stable``, ``insiders``
                or a version such as ``1.141.0``. Builds are verified and cached
                as by ``Get VS Code Executable`` from ``VSCode.Helper``.
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
          - ``cache_dir``: Directory for downloaded builds. Defaults to
                ``robotframework-vscode/vscode`` in the user's cache directory.
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
        self._instances()[ids[0]] = Instance(Path(executable), directories)
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

    @keyword("Install VS Code Extension")
    def install_vs_code_extension(
        self, extension: str, browser: SelectionType | str = SelectionType.CURRENT
    ) -> None:
        """Installs an extension into a running VS Code instance started with `Open VS Code`.

        The extension is installed the way ``extensions`` of `Open VS Code`
        installs it before the start: with the instance's command-line script,
        into the instance's own extensions directory, so neither the user's
        VS Code nor other instances get it. Forks of VS Code install from
        their own extension gallery. The keyword returns when the installation
        has finished. VS Code picks the extension up shortly afterwards,
        without a restart. A command palette that is already open does not
        list the new extension's commands, so tests that run one retry with
        a freshly opened palette, for example with ``Wait Until Keyword Succeeds``.

        *Arguments:*
          - ``extension``: A Marketplace identifier such as ``ms-python.python``,
                or the path of a ``.vsix`` file.
          - ``browser``: ``CURRENT`` for the active instance, or a browser id
                that `Open VS Code` returned.

        Example:
        | `Open VS Code`    ${EXECDIR}/tests/workspace
        | `Install VS Code Extension`    ms-python.python
        | `Install VS Code Extension`    ${EXECDIR}/dist/my-extension.vsix
        """
        if SelectionType.create(browser) is SelectionType.CURRENT:
            active = self.get_browser_ids(SelectionType.CURRENT)
            browser_id = active[0] if active else "CURRENT"
        else:
            browser_id = str(browser)
        instance = self._instances().get(browser_id)
        if instance is None:
            raise ValueError(
                f"Browser '{browser_id}' is not a VS Code instance started by 'Open VS Code'; "
                "only those can install extensions."
            )
        install_extension(
            cli_path(instance.executable), extension, instance.directories, instance_environment(os.environ)
        )
        logger.info(f"Installed extension {extension} into the VS Code instance {instance.directories.root}")


VSCode.__doc__ = cleandoc(_INTRO) + "\n\n" + cleandoc(Electron.__doc__ or "")

__all__ = ["VSCode"]
