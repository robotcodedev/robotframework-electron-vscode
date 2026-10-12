"""Robot Framework library for end-to-end testing of VS Code extensions."""

import functools
import os
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any, NamedTuple

from Browser.utils import logger
from Browser.utils.data_types import ColorScheme, ElementState, NewPageDetails, RecordHar, SelectionType
from robot.utils import DotDict
from robotlibcore import keyword

from Electron import Electron, RecordVideo
from Electron._docs import importing, shared_sections

from .download import select_build
from .instance import (
    InstanceDirectories,
    create_instance_directories,
    instance_environment,
    launch_arguments,
    remove_instance_directories,
    write_settings,
)

__version__ = version("robotframework-vscode")

_INTRO = """
VSCode library is a Robot Framework library for end-to-end testing of VS Code extensions.

It is built on the Electron library and the
[https://robotframework-browser.org|Browser library]: Browser keywords, such as
`Click` and `Get Text`, act on the workbench, and the keywords of the Electron
library work for VS Code instances. Import ``VSCode`` instead of ``Browser`` or
``Electron``. The library hides Browser's keywords for browsers and contexts,
see `Browser, Context and Page`. Guides and an example project are on the
[https://robotcodedev.github.io/robotframework-electron-vscode/|documentation site].

= Opening VS Code =

`Open VS Code` starts an isolated VS Code instance with the extension under
test and returns once the workbench is ready. It downloads the requested
VS Code version into a cache if needed, or starts an installed VS Code or a
fork. Each instance gets its own user data and extensions directories under the
output directory, so neither your own VS Code nor other instances affect it.

| ${vscode}    ${_} =    `Open VS Code`    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}

= Extensions =

Extensions that the extension under test depends on come from an extensions
directory given as ``extensions_dir``, which ``Execute VS Code CLI Command``
from ``VSCode.Helper`` has filled. `Get VS Code Instance Directories` returns
the directories of a running instance. The guide on extensions shows these and
other ways, such as installing into a running instance.

= The workbench =

The workbench window is a page, and windows that VS Code opens later are pages
too. The library has no keywords for the command palette, notifications or
other parts of the workbench. Their DOM changes with VS Code releases and
differs between forks, so these keywords and their locators belong to your
project. The documentation site shows how to write them.

= Several instances =

Several instances can be open at once. `Switch Electron Application` makes
another one the active instance, and `Get Electron Application Ids` returns
their ids.

= Closing VS Code =

`Close VS Code` ends an instance. Automatic closing ends it with the test or
suite that opened it, see `Automatic page and context closing`.

= The main process, videos, traces and HAR files =

`Evaluate In Main Process` runs a JavaScript function in VS Code's main
process. `Open VS Code` takes ``record_video``, ``tracing`` and ``record_har``,
and the launch options ``color_scheme``, ``locale``, ``timezone_id`` and
``bypass_csp``, as `New Electron Application` does.

= VS Code without starting it =

``Get VS Code Executable`` of the ``VSCode.Helper`` library downloads VS Code
and returns its executable, for example in a setup step of a CI job.
"""


class Instance(NamedTuple):
    executable: Path
    directories: InstanceDirectories


class VSCode(Electron):
    ROBOT_LIBRARY_VERSION = __version__

    _instance_cleanup_done = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    # Libdoc and robotlibcore take the signature and the types of the import arguments
    # from Browser through __wrapped__. A decorator would hide __init__ from mypy.
    functools.update_wrapper(__init__, Electron.__init__)
    __init__.__doc__ = importing("VSCode")

    def _start_suite(self, name: str, attrs: dict[str, Any]) -> None:
        super()._start_suite(name, attrs)
        # Like Browser's output folders: once per process, before the run opens its first instance.
        if not VSCode._instance_cleanup_done:
            VSCode._instance_cleanup_done = True
            remove_instance_directories(Path(self.outputdir))

    def _instances(self) -> dict[str, Instance]:
        """The instances of `Open VS Code` that are still open, by id."""
        instances: dict[str, Instance] = self.__dict__.setdefault("_vscode_instances", {})
        if instances:
            for closed in instances.keys() - set(self.get_browser_ids(SelectionType.ALL)):
                del instances[closed]
        return instances

    @keyword("Open VS Code")
    def open_vs_code(
        self,
        path: Path | None = None,
        *,
        version: str = "stable",
        executable: Path | None = None,
        extension_development_path: Path | list[Path] | None = None,
        extensions_dir: Path | None = None,
        settings: dict[str, Any] | None = None,
        args: list[str] | None = None,
        cache_dir: Path | None = None,
        timeout: timedelta = timedelta(seconds=60),
        record_video: RecordVideo | None = None,
        record_har: RecordHar | None = None,
        tracing: bool | Path | None = None,
        color_scheme: ColorScheme | None = None,
        locale: str | None = None,
        timezone_id: str | None = None,
        bypass_csp: bool = False,
    ) -> tuple[str, NewPageDetails]:
        """Starts an isolated VS Code instance and returns once its workbench is ready.

        Each instance gets its own user-data and extensions directories in
        ``vscode/<n>`` under the output directory, so neither the user's own
        VS Code nor other instances affect it. The directories are kept after
        the instance ends, with VS Code's logs in ``user-data/logs``.
        Variables that tie a process to a running VS Code (``VSCODE_*`` and
        ``ELECTRON_RUN_AS_NODE``) are removed from the instance's environment.

        The instance is an application as started by `New Electron
        Application`: its workbench window is the active page, Browser
        keywords work on it, and `Close VS Code` and automatic closing end
        it.

        *Arguments:*
          - ``path``: A folder to open as workspace, or a file to open in an editor.
          - ``version``: VS Code to download and start: ``stable``, ``insiders``
                or a version such as ``1.141.0``. Builds are verified and cached
                as by ``Get VS Code Executable`` from ``VSCode.Helper``.
          - ``executable``: An installed VS Code executable to start instead,
                as a path or as a command found on ``PATH``. Symbolic links are
                followed. Nothing is downloaded then.
          - ``extension_development_path``: Folder of the extension under test,
                or a list of folders. They are loaded as development extensions.
          - ``extensions_dir``: An extensions directory to use instead of an
                empty one of the instance, for example one prepared with
                ``Execute VS Code CLI Command`` from ``VSCode.Helper``. VS Code
                writes into this directory while it runs, so give each
                instance its own copy. A relative path is relative to the
                working directory of the test run.
          - ``settings``: User settings for the instance. They override the
                defaults, which switch off the welcome page, update checks,
                telemetry, workspace trust, the screen reader mode and the
                secondary side bar.
          - ``args``: Additional command-line arguments for VS Code.
          - ``cache_dir``: Directory for downloaded builds. Defaults to
                ``robotframework-vscode/vscode`` in the user's cache directory.
          - ``timeout``: How long to wait for the window and for the workbench.
          - ``record_video``: Records a video of the instance's windows, as for
                `New Electron Application`. VS Code's window keeps its own size,
                so for a full frame give the video a ``size`` and call
                `Set Viewport Size` with the same size after the start.
          - ``record_har``: Records the network traffic of the workbench into a
                HAR file, as for `New Electron Application`.
          - ``tracing``: Records a Playwright trace of the workbench, as for
                `New Electron Application`.
          - ``color_scheme``: The color scheme that the windows report for
                ``prefers-color-scheme``, as for `New Electron Application`.
                VS Code's theme comes from its settings, not from this option.
          - ``locale``: The locale of the windows, as for
                `New Electron Application`. It sets their number and date
                formats, but not VS Code's display language, which comes from
                ``--locale`` in ``args`` and a language pack.
          - ``timezone_id``: The time zone of the windows, as for
                `New Electron Application`.
          - ``bypass_csp``: Bypasses the Content Security Policy of the
                windows, as for `New Electron Application`. `Record Selector`
                needs it, because the workbench requires Trusted Types for
                scripts.

        *Returns:*
          A tuple of the instance's id and the page details of the workbench
          window, as `New Electron Application` returns them.

        *Raises:*
          - ``ValueError``: The version does not exist for the current
                platform, the download does not match its checksum, or the
                executable is not found.

        Example:
        | ${vscode}    ${_} =    `Open VS Code`    ${EXECDIR}/tests/workspace    extension_development_path=${EXECDIR}
        | `Open VS Code`    version=1.141.0    settings=${{ {"window.title": "robot-test"} }}
        """
        executable, product = select_build(version, executable, cache_dir)
        directories = create_instance_directories(Path(self.outputdir), extensions_dir)
        write_settings(directories.user_data, settings)
        env = instance_environment(os.environ)
        if isinstance(extension_development_path, Path):
            extension_development_path = [extension_development_path]
        arguments = launch_arguments(directories, extension_development_path or [], args or [], path)
        logger.info(f"Starting VS Code {product or executable} with instance directory {directories.root}")
        instance, page = self.new_electron_application(
            executable,
            args=arguments,
            env=env,
            timeout=timeout,
            record_video=record_video,
            record_har=record_har,
            tracing=tracing,
            color_scheme=color_scheme,
            locale=locale,
            timezone_id=timezone_id,
            bypass_csp=bypass_csp,
        )
        try:
            self.wait_for_elements_state(".monaco-workbench", ElementState.visible, timeout)
        except Exception:
            try:
                self.close_browser(instance)
            except Exception as error:  # noqa: BLE001 - the error of the workbench is the one to report
                logger.warn(f"Closing the VS Code instance {instance} failed: {error}")
            raise
        self._instances()[instance] = Instance(Path(executable), directories)
        return instance, page

    @keyword("Close VS Code")
    def close_vs_code(self, instance: SelectionType | str = SelectionType.CURRENT) -> None:
        """Ends a VS Code instance started with `Open VS Code`.

        The keyword returns after the VS Code process has exited. It behaves
        like `Close Electron Application`.

        *Arguments:*
          - ``instance``: The id that `Open VS Code` returned. ``CURRENT``
                ends the active instance, ``ALL`` ends all instances and
                applications.

        Example:
        | ${vscode}    ${_} =    `Open VS Code`
        | `Close VS Code`    ${vscode}
        | `Close VS Code`    ALL
        """
        self.close_electron_application(instance)

    @keyword("Get VS Code Instance Directories")
    def get_vs_code_instance_directories(self, instance: SelectionType | str = SelectionType.CURRENT) -> DotDict:
        """Returns the directories of a VS Code instance started with `Open VS Code`.

        Pass them to ``Execute VS Code CLI Command`` from ``VSCode.Helper`` to
        install, uninstall or list the instance's extensions, or read VS Code's
        logs in ``logs`` of the user-data directory. A running VS Code may not
        notice what the command-line script changes in its extensions
        directory; the guide on extensions shows how to wait until it does.

        *Arguments:*
          - ``instance``: ``CURRENT`` for the active instance, or an id that
                `Open VS Code` returned.

        *Returns:*
          A dictionary with the instance's folder as ``root``, its user-data
          directory as ``user_data`` and its extensions directory as
          ``extensions``, which is ``extensions_dir`` of `Open VS Code` if it
          was given. Both ``${dirs.extensions}`` and ``${dirs}[extensions]``
          work.

        *Raises:*
          - ``ValueError``: The id is not an open VS Code instance started
                with `Open VS Code`.

        Example:
        | ${dirs} =    `Get VS Code Instance Directories`
        | ${list} =    Execute VS Code CLI Command    ${dirs.extensions}    ${dirs.user_data}    --list-extensions
        """
        directories = self._instance(instance).directories
        return DotDict(
            root=str(directories.root), user_data=str(directories.user_data), extensions=str(directories.extensions)
        )

    def _instance(self, instance: SelectionType | str) -> Instance:
        """The instance of `Open VS Code` with the id ``instance``, or the active one for ``CURRENT``."""
        if SelectionType.create(instance) is SelectionType.CURRENT:
            active = self.get_browser_ids(SelectionType.CURRENT)
            instance_id = active[0] if active else "CURRENT"
        else:
            instance_id = str(instance)
        found = self._instances().get(instance_id)
        if found is None:
            raise ValueError(f"'{instance_id}' is not an open VS Code instance started by 'Open VS Code'.")
        return found


VSCode.__doc__ = cleandoc(_INTRO) + "\n\n" + shared_sections("`Open VS Code`", "`Close VS Code`")

__all__ = ["VSCode"]
