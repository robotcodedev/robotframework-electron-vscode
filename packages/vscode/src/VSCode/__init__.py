"""Robot Framework library for end-to-end testing of VS Code extensions."""

import functools
import os
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any, NamedTuple

from Browser.utils import logger
from Browser.utils.data_types import ColorScheme, ElementState, NewPageDetails, RecordHar, RecordVideo, SelectionType
from robot.utils import DotDict
from robotlibcore import keyword

from Electron import Electron
from Electron._docs import importing, shared_sections

from .extension_host import (
    PAGE_WORKSPACE_ID,
    PageNotReadyError,
    UnknownWorkspaceError,
    run_in_extension_host,
)
from .instance import (
    DIRECTORY_OPTIONS,
    InstanceDirectories,
    cli_environment,
    cli_path,
    create_instance_directories,
    installed_executable,
    instance_environment,
    launch_arguments,
    product_version,
    remove_instance_directories,
    run_cli,
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

= Starting VS Code =

`Start VS Code` starts an isolated VS Code instance from a VS Code executable,
with the extension under test, and returns once the workbench is ready. The
library downloads nothing: the VS Code belongs to the test environment, for
example an installation, a portable copy, a fork, or a build that
``@vscode/test-electron`` downloaded. A variable, for example in
``robot.toml``, keeps its path out of the tests.

| ${vscode}    ${_} =    `Start VS Code`    ${VSCODE_EXECUTABLE}    ${EXECDIR}/tests/workspace
| ...    extension_development_path=${EXECDIR}

= Instance directories =

Each instance gets its own user-data and extensions directories in
``vscode/<n>`` under the output directory, so neither your own VS Code nor
other instances affect it. ``user_data_dir`` and ``extensions_dir`` give
prepared directories instead, which the instance uses as they are. The library
writes its default settings only into user-data directories that it creates.
`Get VS Code Instance Directories` returns the directories of an instance.

= Extensions and the command-line script =

`Execute VS Code CLI Command` runs VS Code's command-line script, for example
to install an extension that the extension under test depends on. Without
``executable``, it works on the active instance. With ``executable`` and the
directories, it prepares them before VS Code starts, as `Start VS Code` gets
them. The guide on extensions shows these and other ways, such as installing
into a running instance.

= The workbench =

The workbench window is a page, and windows that VS Code opens later are pages
too. `Switch Window` switches between them by their titles, and the window
keywords size and maximise them, see `Windows and pages`. The library has no
keywords for the command palette, notifications or other parts of the
workbench. Their DOM changes with VS Code releases and
differs between forks, so these keywords and their locators belong to your
project. The documentation site shows how to write them.

= The extension host =

VS Code runs the extensions of a workbench window in its extension host,
where the ``vscode`` module gives access to the extension API.
`Evaluate In Extension Host` runs a JavaScript function there, to prepare a
test or to wait for a state, for example to run a command by its id or to wait
for the diagnostics of a language server. Check the outcome through the
workbench.

The keyword works through a small helper extension. The package contains it
twice, next to the library's ``__init__.py``: as the folder ``extension`` and
as the file ``extension-host.vsix``. The library does not load it: like the
extensions under test, it is part of the test environment. Load it in one of
two ways:

- As a development extension: give the folder to `Start VS Code` in
  ``extension_development_path``, after your own extensions. Nothing is
  installed, and the folder always fits the installed library. The window is
  then an "Extension Development Host": its title starts with
  ``[Extension Development Host]``, also without an extension of your own,
  and ``vscode.extensions.all`` lists the helper.
- Installed: install the ``.vsix`` into an extensions directory before the
  start, for example with `Execute VS Code CLI Command` and ``executable``,
  and give the directory to `Start VS Code` as ``extensions_dir``. VS Code
  then runs without development mode. Install the ``.vsix`` again after an
  update of the library: `Evaluate In Extension Host` fails while the
  versions differ.

In Robot Framework data, inline Python gives the folder's path, also in a
``*** Variables ***`` section:

| ${HELPER_EXTENSION}    ${{ pathlib.Path(VSCode.__file__).parent / 'extension' }}

In a shell, this prints the path of the ``.vsix``:

| python -c "import pathlib, VSCode; print(pathlib.Path(VSCode.__file__).parent / 'extension-host.vsix')"

= Several instances =

Several instances can be open at once. `Switch Electron Application` makes
another one the active instance, and `Get Electron Application Ids` returns
their ids.

= Closing VS Code =

`Close VS Code` ends an instance. Automatic closing ends it with the test or
suite that opened it, see `Automatic page and context closing`.

= The main process, videos, traces and HAR files =

`Evaluate In Main Process` runs a JavaScript function in VS Code's main
process. `Start VS Code` takes ``record_video``, ``tracing`` and ``record_har``,
and the launch options ``color_scheme``, ``locale``, ``timezone_id`` and
``bypass_csp``, as `Start Electron Application` does.
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
        """The instances of `Start VS Code` that are still open, by id."""
        instances: dict[str, Instance] = self.__dict__.setdefault("_vscode_instances", {})
        if instances:
            for closed in instances.keys() - set(self.get_browser_ids(SelectionType.ALL)):
                del instances[closed]
        return instances

    @keyword("Start VS Code")
    def start_vs_code(
        self,
        executable: Path,
        path: Path | None = None,
        *,
        extension_development_path: Path | list[Path] | None = None,
        extensions_dir: Path | None = None,
        user_data_dir: Path | None = None,
        settings: dict[str, Any] | None = None,
        args: list[str] | None = None,
        timeout: timedelta = timedelta(seconds=60),
        record_video: RecordVideo | None = None,
        record_har: RecordHar | None = None,
        tracing: bool | Path | None = None,
        color_scheme: ColorScheme | None = None,
        locale: str | None = None,
        timezone_id: str | None = None,
        bypass_csp: bool = False,
    ) -> tuple[str, NewPageDetails]:
        """Starts an isolated VS Code instance from ``executable`` and returns once its workbench is ready.

        The library downloads nothing: the VS Code to start belongs to the
        test environment, for example an installation, a portable copy, a
        fork, or a build that ``@vscode/test-electron`` downloaded.

        Each instance gets its own user-data and extensions directories in
        ``vscode/<n>`` under the output directory, unless ``user_data_dir``
        or ``extensions_dir`` give them, so neither the user's own VS Code
        nor other instances affect it. The directories are kept after the
        instance ends, with VS Code's logs in ``logs`` of the user-data
        directory. Tests that run in VS Code's terminal or test explorer start
        an instance that the surrounding VS Code does not affect.

        The instance is an application as started by `Start Electron
        Application`: its workbench window is the active page, Browser
        keywords work on it, and `Close VS Code` and automatic closing end
        it.

        *Arguments:*
          - ``executable``: VS Code's executable, such as the path that
                ``@vscode/test-electron`` returns, not its command-line script
                ``bin/code``. A command on ``PATH`` and symbolic links work when
                they lead to the executable. A relative path is relative to the
                working directory of the test run.
          - ``path``: A folder to open as workspace, or a file to open in an editor.
          - ``extension_development_path``: Folder of the extension under test,
                or a list of folders. They are loaded as development extensions.
          - ``extensions_dir``: An extensions directory to use instead of an
                empty one of the instance, for example one prepared with
                `Execute VS Code CLI Command`. VS Code writes into this
                directory while it runs, so give each instance its own copy. A
                relative path is relative to the working directory of the test
                run.
          - ``user_data_dir``: A user-data directory to use instead of a new
                one of the instance, for example one with prepared settings.
                VS Code writes into it while it runs, as into
                ``extensions_dir``. The keyword writes no settings into it, so
                take over the default settings that ``settings`` describes.
                A relative path is relative to the working directory of the
                test run.
          - ``settings``: User settings for the user-data directory that the
                keyword creates. They override the defaults:
                ``workbench.startupEditor: none``, ``update.mode: none``,
                ``telemetry.telemetryLevel: off``,
                ``extensions.autoUpdate: false``,
                ``extensions.autoCheckUpdates: false``,
                ``security.workspace.trust.enabled: false``,
                ``editor.accessibilitySupport: off``, without which VS Code
                detects a screen reader under Playwright, and
                ``workbench.secondarySideBar.defaultVisibility: hidden``.
                Cannot be combined with ``user_data_dir``.
          - ``args``: Additional command-line arguments for VS Code.
          - ``timeout``: How long to wait for the window and for the workbench.
          - ``record_video``: Records a video of the instance's windows, as for
                `Start Electron Application`. VS Code's window keeps its own size,
                so for a full frame give the video a ``size`` and call
                `Set Viewport Size` with the same size after the start.
          - ``record_har``: Records the network traffic of the workbench into a
                HAR file, as for `Start Electron Application`.
          - ``tracing``: Records a Playwright trace of the workbench, as for
                `Start Electron Application`.
          - ``color_scheme``: The color scheme that the windows report for
                ``prefers-color-scheme``, as for `Start Electron Application`.
                VS Code's theme comes from its settings, not from this option.
          - ``locale``: The locale of the windows, as for
                `Start Electron Application`. It sets their number and date
                formats, but not VS Code's display language, which comes from
                ``--locale`` in ``args`` and a language pack.
          - ``timezone_id``: The time zone of the windows, as for
                `Start Electron Application`.
          - ``bypass_csp``: Bypasses the Content Security Policy of the
                windows, as for `Start Electron Application`. `Record Selector`
                needs it, because the workbench requires Trusted Types for
                scripts.

        *Returns:*
          A tuple of the instance's id and the page details of the workbench
          window, as `Start Electron Application` returns them.

        *Raises:*
          - ``ValueError``: The executable is not found, or ``settings`` is
                given together with ``user_data_dir``.

        Example:
        | ${vscode}    ${_} =    `Start VS Code`    ${VSCODE_EXECUTABLE}    ${EXECDIR}/tests/workspace
        | ...    extension_development_path=${EXECDIR}
        | `Start VS Code`    /usr/share/code/code    settings=${{ {"window.title": "robot-test"} }}
        | Copy Directory    ${EXECDIR}/tests/user-data    ${OUTPUT_DIR}/user-data
        | `Start VS Code`    ${VSCODE_EXECUTABLE}    user_data_dir=${OUTPUT_DIR}/user-data
        """
        if settings is not None and user_data_dir is not None:
            raise ValueError(
                "'settings' cannot be combined with 'user_data_dir': the keyword writes no settings into a given "
                "user-data directory. Put them into its User/settings.json instead."
            )
        found = installed_executable(Path(executable))
        directories = create_instance_directories(Path(self.outputdir), extensions_dir, user_data_dir)
        if user_data_dir is None:
            write_settings(directories.user_data, settings)
        env = instance_environment(os.environ)
        if isinstance(extension_development_path, Path):
            extension_development_path = [extension_development_path]
        arguments = launch_arguments(directories, extension_development_path or [], args or [], path)
        logger.info(f"Starting VS Code {product_version(found) or found} with instance directory {directories.root}")
        instance, page = self.start_electron_application(
            found,
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
        self._instances()[instance] = Instance(found, directories)
        return instance, page

    @keyword("Close VS Code")
    def close_vs_code(self, instance: SelectionType | str = SelectionType.CURRENT) -> None:
        """Ends a VS Code instance started with `Start VS Code`.

        The keyword returns after the VS Code process has exited. It behaves
        like `Close Electron Application`.

        *Arguments:*
          - ``instance``: The id that `Start VS Code` returned. ``CURRENT``
                ends the active instance, ``ALL`` ends all instances and
                applications.

        Example:
        | ${vscode}    ${_} =    `Start VS Code`    ${VSCODE_EXECUTABLE}
        | `Close VS Code`    ${vscode}
        | `Close VS Code`    ALL
        """
        self.close_electron_application(instance)

    @keyword("Get VS Code Instance Directories")
    def get_vs_code_instance_directories(self, instance: SelectionType | str = SelectionType.CURRENT) -> DotDict:
        """Returns the directories of a VS Code instance started with `Start VS Code`.

        Use them to read VS Code's logs in ``logs`` of the user-data
        directory, or to look into the extensions directory.
        `Execute VS Code CLI Command` works on the directories of the active
        instance by itself.

        *Arguments:*
          - ``instance``: ``CURRENT`` for the active instance, or an id that
                `Start VS Code` returned.

        *Returns:*
          A dictionary with the instance's folder as ``root``, its user-data
          directory as ``user_data`` and its extensions directory as
          ``extensions``, which are ``user_data_dir`` and ``extensions_dir``
          of `Start VS Code` if they were given. Both ``${dirs.extensions}``
          and ``${dirs}[extensions]`` work.

        *Raises:*
          - ``ValueError``: The id is not an open VS Code instance started
                with `Start VS Code`.

        Example:
        | ${dirs} =    `Get VS Code Instance Directories`
        | ${installed} =    List Directories In Directory    ${dirs.extensions}    ms-python.python-*
        """
        directories = self._instance(instance).directories
        return DotDict(
            root=str(directories.root), user_data=str(directories.user_data), extensions=str(directories.extensions)
        )

    @keyword("Execute VS Code CLI Command")
    def execute_vs_code_cli_command(
        self,
        *args: str,
        executable: Path | None = None,
        user_data_dir: Path | None = None,
        extensions_dir: Path | None = None,
    ) -> str:
        """Runs VS Code's command-line script with ``args`` and returns its output.

        Use it to install, uninstall, list or update extensions, see
        ``code --help`` for all arguments. The script runs in one of two
        environments:

        - Without ``executable``, ``user_data_dir`` and ``extensions_dir``: the
          script of the active VS Code instance, on that instance's
          directories. A running VS Code may not notice at once what the
          script changes in its extensions directory; the guide on extensions
          shows how to wait until it does.
        - With ``executable``: the environment that `Start VS Code` gets with
          the same ``executable``, ``user_data_dir`` and ``extensions_dir``.
          Given directories are used as they are, and the others are created
          fresh in a new ``vscode/<n>`` folder under the output directory, so
          that a call never changes the user's own VS Code. Use it to prepare
          an extensions directory before VS Code starts.

        A call from VS Code's terminal or test explorer does not reach the
        surrounding VS Code. Without a command, VS Code's script starts VS
        Code's window instead, so the keyword refuses a call without arguments
        or with an empty one, and on Linux it runs the script without a
        display, so that no window can open.

        *Arguments:*
          - ``args``: The arguments of the script, without
                ``--extensions-dir`` and ``--user-data-dir``.
          - ``executable``: The VS Code executable whose script runs, as for
                `Start VS Code`.
          - ``user_data_dir``: The user-data directory the script works on, as
                for `Start VS Code`. Needs ``executable``.
          - ``extensions_dir``: The extensions directory the script works on, as
                for `Start VS Code`. Needs ``executable``.

        *Returns:*
          The standard output of the script.

        *Raises:*
          - ``ValueError``: ``args`` are missing, one of them is empty, or they
                contain ``--extensions-dir`` or ``--user-data-dir``; a directory
                is given without ``executable``; no VS Code instance is open and
                ``executable`` is not given; or the VS Code or its command-line
                script is not found.
          - ``RuntimeError``: The script ends with an error or does not finish
                within 10 minutes.

        Example:
        | `Execute VS Code CLI Command`    --install-extension    ms-python.python
        | ${list} =    `Execute VS Code CLI Command`    --list-extensions
        | `Execute VS Code CLI Command`    --install-extension    ms-python.python
        | ...    executable=${VSCODE_EXECUTABLE}    extensions_dir=${CACHE}/extensions
        | ...    user_data_dir=${CACHE}/user-data
        """
        if not args:
            raise ValueError(
                "Execute VS Code CLI Command needs the script's arguments, such as '--install-extension' and an "
                "extension. Without a command, VS Code's script would open a window."
            )
        for number, arg in enumerate(args, 1):
            if not str(arg).strip():
                raise ValueError(
                    f"Argument {number} of the script is empty. VS Code's script would ignore it, and without a "
                    "command it opens a window."
                )
            if str(arg).split("=", 1)[0] in DIRECTORY_OPTIONS:
                raise ValueError(
                    f"The script cannot get '{arg}': it works on the directories of the active instance, or on "
                    "'extensions_dir' and 'user_data_dir' together with 'executable'."
                )
        if executable is None:
            if user_data_dir is not None or extensions_dir is not None:
                raise ValueError(
                    "'user_data_dir' and 'extensions_dir' need 'executable'. Without them, the keyword works on the "
                    "active VS Code instance."
                )
            no_instance = "Give 'executable' to run the script without an instance."
            # Without an instance, Browser is not asked for the active one, which would start its Playwright process.
            if not self._instances():
                raise ValueError(f"No VS Code instance is open. {no_instance}")
            try:
                instance = self._instance(SelectionType.CURRENT)
            except ValueError as error:
                raise ValueError(f"{error} {no_instance}") from None
            cli, directories = cli_path(instance.executable), instance.directories
        else:
            cli = cli_path(installed_executable(Path(executable)))
            directories = create_instance_directories(Path(self.outputdir), extensions_dir, user_data_dir)
        return run_cli(cli, directories, args, cli_environment(os.environ))

    @keyword("Evaluate In Extension Host")
    def evaluate_in_extension_host(
        self, function: str, *lines: str, arg: Any = None, workspace: Path | None = None
    ) -> Any:
        """Runs a JavaScript function in VS Code's extension host and returns its result.

        The extension host runs the extensions of a workbench window. There,
        the ``vscode`` module gives access to VS Code's extension API. Use it
        to prepare a test and to wait for a state, for example to run a
        command by its id, to wait for the diagnostics of a language server or
        to read the text of an editor, and check the outcome through the
        workbench. The function runs in the library's helper extension, which
        the test loads, as a development extension or installed, see
        `The extension host`.

        Each workbench window has an extension host of its own. Without
        ``workspace``, the keyword takes the one of the window that shows the
        active page; `Switch Window` changes it. A window into which an editor
        was moved belongs to the window that the editor came from.

        The keyword waits up to the library's timeout for the extension host,
        for example right after `Start VS Code` or after the window reloads,
        and then again up to the timeout for the function. A function that
        takes longer keeps running in the extension host.

        A command that opens a quick pick or an input box settles only once
        it is answered. Start such a command with ``void`` instead of
        returning its promise, so that the keyword returns at once.

        *Arguments:*
          - ``function``: A JavaScript function as text, or its first line.
                It gets two parameters: the ``vscode`` module and ``arg``.
                It may return a promise.
          - ``lines``: Further lines of the function. They are joined to
                ``function`` with line breaks, so that a function can span
                several cells with ``...``.
          - ``arg``: A JSON-serialisable value that the function gets.
          - ``workspace``: The folder or the ``.code-workspace`` file that a
                window has open, to select that window instead of the one of
                the active page. A relative path is relative to the working
                directory of the test run.

        *Returns:*
          The function's result, which must be JSON-serialisable. ``None`` if
          the function returns nothing.

        *Raises:*
          - ``ValueError``: ``arg`` is not JSON-serialisable.
          - ``AssertionError``: No VS Code instance is open, the active
                application was not started by `Start VS Code`, the window
                cannot be determined, no extension host answers within the
                timeout, for example because the helper extension is not
                loaded, the helper extension has another version than the
                library, or the function throws an error, does not finish
                within the timeout or returns a value that is not
                JSON-serialisable.

        Example:
        | `Evaluate In Extension Host`    (vscode) => vscode.commands.executeCommand('myExtension.refresh')
        | ${text} =    `Evaluate In Extension Host`    (vscode) => vscode.window.activeTextEditor?.document.getText()
        | `Evaluate In Extension Host`    (vscode) => {
        | ...    void vscode.commands.executeCommand('workbench.action.quickOpen');
        | ...    }
        | ${count} =    `Evaluate In Extension Host`    (vscode, path) =>
        | ...    vscode.languages.getDiagnostics(vscode.Uri.file(path)).length
        | ...    arg=${EXECDIR}/tests/workspace/src/example.py
        """
        try:
            user_data = self._instance(SelectionType.CURRENT).directories.user_data
        except ValueError as error:
            # The active application is no argument here, so this fails like a check, as in Evaluate In Main Process.
            raise AssertionError(str(error)) from None
        script = "\n".join((function, *lines))
        return run_in_extension_host(user_data, script, arg, workspace, self._page_workspace_id, self.timeout / 1000)

    def _page_workspace_id(self) -> str | None:
        """VS Code's id of the workspace of the active page's workbench window, ``None`` for an empty window."""
        try:
            found = self.evaluate_javascript(None, PAGE_WORKSPACE_ID)
        except AssertionError as error:
            # Browser reports the page's errors so, for example while the window reloads and its page navigates.
            raise PageNotReadyError(str(error)) from error
        if not isinstance(found, dict):
            raise UnknownWorkspaceError
        workspace_id: str | None = found["workspaceId"]
        return workspace_id

    def _instance(self, instance: SelectionType | str) -> Instance:
        """The instance of `Start VS Code` with the id ``instance``, or the active one for ``CURRENT``."""
        if SelectionType.create(instance) is SelectionType.CURRENT:
            active = self.get_browser_ids(SelectionType.CURRENT)
            if not active:
                raise ValueError("No VS Code instance is open.")
            instance_id = active[0]
        else:
            instance_id = str(instance)
        found = self._instances().get(instance_id)
        if found is None:
            raise ValueError(f"'{instance_id}' is not an open VS Code instance started by 'Start VS Code'.")
        return found


VSCode.__doc__ = cleandoc(_INTRO) + "\n\n" + shared_sections("`Start VS Code`", "`Close VS Code`")

__all__ = ["VSCode"]
