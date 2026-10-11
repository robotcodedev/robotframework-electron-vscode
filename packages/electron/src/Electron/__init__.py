"""Robot Framework library for testing Electron applications, built on the Browser library."""

import functools
import os
import shutil
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any, TypedDict

from Browser import Browser
from Browser.utils import logger
from Browser.utils.data_types import ColorScheme, NewPageDetails, RecordHar, SelectionType, ViewportDimensions
from robotlibcore import keyword

from ._docs import browser_import_arguments, browser_sections

__version__ = version("robotframework-electron")

_JS_MODULE = Path(__file__).with_name("electron.js")

_INTRO = """
Electron library is a Robot Framework library for testing Electron applications.

It is built on the [https://robotframework-browser.org|Browser library] and
contains every Browser keyword. Import ``Electron`` instead of ``Browser``. It
takes the same import arguments, see `Importing`. Guides and examples are on the
[https://robotcodedev.github.io/robotframework-electron-vscode/|documentation site].

= Starting an application =

`New Electron Application` starts an application and waits for its first
window. Pass the application's executable, or for an application that the plain
Electron binary runs, the Electron executable and the application folder in
``args``. ``Get Electron Executable`` of the ``Electron.Helper`` library
downloads an Electron release and returns its executable.

| `New Electron Application`    /opt/my-app/my-app
| `Get Title`    ==    My App
| `Click`    text=Settings

= Windows and pages =

The application becomes a browser with one context, and each of its windows is
a page of that context, see `Browser, Context and Page`. The first window is the
active page, and windows that the application opens later can be selected with
`Switch Page`. `Get Browser Catalog` lists the application with the type
``electron``.

= Closing an application =

`Close Electron Application` ends an application. `Close Browser`,
`Close Context` and automatic closing end it as well, see
`Automatic page and context closing`.

= Videos, traces and HAR files =

`New Electron Application` records a video of the windows with
``record_video``, a Playwright trace with ``tracing``, and the network traffic
of the windows with ``record_har``. They are saved when the application closes.

= Browser keywords =

Browser keywords work on the windows as on any other page. The following
sections come from the Browser library's documentation.
"""

_IMPORTING = """
Electron library takes the same import arguments as the Browser library.

They configure the Browser keywords, for example their timeout or presenter
mode, and apply to the windows of Electron applications as to any other page.
All arguments are named arguments.

Example:
| Library    Electron    timeout=20s    enable_presenter_mode=True
"""


class ShowActions(TypedDict, total=False):
    """Overlay of the performed actions in a video, as Playwright's ``recordVideo.showActions``.

    - ``duration``: How long each action is shown, in milliseconds.
    - ``position``: Where the overlay is shown: ``top-left``, ``top``,
      ``top-right``, ``bottom-left``, ``bottom`` or ``bottom-right``.
    - ``fontSize``: Font size of the overlay, in pixels.
    - ``cursor``: ``pointer`` shows the mouse cursor, ``none`` hides it.
    """

    duration: int
    position: str
    fontSize: int
    cursor: str


class RecordVideo(TypedDict, total=False):
    """Video recording of an Electron application's windows.

    The keys ``dir`` and ``size`` work as for Browser's ``recordVideo`` of
    `New Context`, ``showActions`` is Playwright's overlay of the performed
    actions.

    - ``dir``: Folder for the videos. Relative paths are relative to
      Browser's video folder ``browser/video`` in the output directory,
      which is also the default.
    - ``size``: Size of the video, as a dictionary with ``width`` and
      ``height``. Defaults to 1280x720. A larger window is scaled down to
      fit, a smaller one is shown at its own size with a grey margin.
    - ``showActions``: Shows the performed actions in the video: a
      dictionary with ``duration`` (milliseconds), ``position``,
      ``fontSize`` and ``cursor``.

    Example:
    | `New Electron Application`    ${ELECTRON}    record_video={'size': {'width': 1920, 'height': 1080}}
    | `New Electron Application`    ${ELECTRON}    record_video={'showActions': {'duration': 800}}
    """

    dir: str
    size: ViewportDimensions
    showActions: ShowActions


class Electron(Browser):
    ROBOT_LIBRARY_VERSION = __version__

    _electron_extension_loaded = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    # Libdoc and robotlibcore take the signature and the types of the import arguments
    # from Browser through __wrapped__. A decorator would hide __init__ from mypy.
    functools.update_wrapper(__init__, Browser.__init__)
    __init__.__doc__ = cleandoc(_IMPORTING) + "\n\n" + browser_import_arguments()

    @keyword
    def new_electron_application(
        self,
        executable_path: Path,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        timeout: timedelta | None = None,
        record_video: RecordVideo | None = None,
        record_har: RecordHar | None = None,
        tracing: bool | Path | None = None,
        color_scheme: ColorScheme | None = None,
        locale: str | None = None,
        timezone_id: str | None = None,
        bypass_csp: bool = False,
    ) -> tuple[str, str, NewPageDetails]:
        """Starts an Electron application and makes its first window the active page.

        The application becomes a new active browser with one context. Its
        windows are pages of that context, so Browser keywords like `Click`
        and `Get Text` work on them, and windows the application opens later
        can be selected with `Switch Page`. `Close Electron Application`,
        `Close Browser` and automatic closing end the application.

        *Arguments:*
          - ``executable_path``: The Electron executable, as a path or as a
                command found on ``PATH``. A relative path is relative to the
                working directory of the test run. For an app that is run by
                the plain Electron binary, pass the app folder in ``args``.
          - ``args``: Command-line arguments for the application.
          - ``env``: Environment variables of the application. If not given,
                the application gets the environment of the test run without
                ``ELECTRON_RUN_AS_NODE``, which runs started from VS Code have
                and which would make Electron run as plain Node.js.
          - ``cwd``: Working directory of the application. A relative path is
                relative to the working directory of the test run, which is
                also the default.
          - ``timeout``: How long to wait for the application to start and
                open its first window. Defaults to the library timeout.
          - ``record_video``: Records a video of the application's windows,
                see `RecordVideo`. An empty dictionary records with the
                defaults. The log embeds the video, and the file is complete
                once the application has closed. Recording needs Playwright's
                ffmpeg, which is installed with Browser's browsers.

          - ``record_har``: Records the network traffic of the application's
                windows into a [http://www.softwareishard.com/blog/har-12-spec/|HAR]
                file, as ``recordHar`` of `New Context`: a dictionary with the
                ``path`` of the file and optionally ``omitContent``. A relative
                path is relative to the output directory. The file is written
                when the application closes.
          - ``tracing``: Records a Playwright trace of the application, as
                ``tracing`` of `New Context`: ``True`` saves it as
                ``browser/traces/trace_{contextid}.zip`` in the output directory,
                and a ``*.zip`` path or a folder saves it there. The variable or
                environment variable ``ROBOT_FRAMEWORK_BROWSER_TRACING`` set to
                ``True`` traces every application. The trace is saved when the
                application closes and shows the keyword calls as groups. Open
                it with ``rfbrowser show-trace /path/to/trace.zip``.
          - ``color_scheme``: The color scheme that the windows report for
                ``prefers-color-scheme``: ``light`` or ``dark``. By default,
                and with ``null``, the application decides, as it does outside
                of tests. Set it for tests that compare screenshots, so that
                they look the same on every machine.
          - ``locale``: The locale of the windows, for example ``de-DE``. It
                sets the language that the pages report and their number and
                date formats. Defaults to the system's. The main process keeps
                the system's locale; ``--lang`` in ``args`` sets it there.
          - ``timezone_id``: The time zone of the windows, for example
                ``Europe/Berlin``. Defaults to the system's. The main process
                keeps the system's time zone; ``TZ`` in ``env`` sets it there.
          - ``bypass_csp``: Bypasses the Content Security Policy of the
                windows, including Trusted Types, as ``bypassCSP`` of
                `New Context`. Features that add scripts to a page need it in
                applications with a strict policy, for example `Record Selector`
                in VS Code. It also applies to webviews and frames, so that
                policy problems of the application go unnoticed. Switch it on
                only where a feature needs it.

        *Returns:*
          A tuple of browser id, context id and page details of the first
          window, like `New Persistent Context`. The page details contain the
          path of the video, or an empty string if no video is recorded.

        *Raises:*
          - ``ValueError``: The executable is not found.

        Example:
        | ${app} =    `New Electron Application`    /opt/my-app/my-app
        | `Get Title`    ==    My App
        | `New Electron Application`    ${ELECTRON}    args=${{ [$EXECDIR + "/app"] }}
        | `New Electron Application`    /opt/my-app/my-app    tracing=True    record_har={'path': 'my-app.har'}
        | `New Electron Application`    /opt/my-app/my-app    color_scheme=dark    locale=de-DE
        """
        found = shutil.which(str(executable_path))
        if found is None:
            raise ValueError(f"Electron executable '{executable_path}' not found.")
        # Browser's Node process runs in Browser's own folder, so it only gets absolute paths.
        executable = os.path.abspath(found)
        if env is None:
            env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE"}
        self._load_electron_extension()
        recording = self.adopted_context_options(tracing=tracing, recordVideo=record_video, recordHar=record_har)
        # Playwright's names. Options that are not given stay out, so that electron.js's defaults apply.
        launch_options = {
            "colorScheme": None if color_scheme is None or color_scheme.name == "null" else color_scheme.name,
            "locale": locale,
            "timezoneId": timezone_id,
            "bypassCSP": bypass_csp or None,
        }
        adopted = self.call_js_keyword(
            "robotframeworkElectronLaunch",
            executablePath=executable,
            args=args or [],
            env=env,
            cwd=os.path.abspath(cwd or os.curdir),
            timeout=self.get_timeout(timeout),
            **recording,
            launchOptions={name: value for name, value in launch_options.items() if value is not None},
            defaultTimeout=int(self.timeout),
        )
        logger.info(f"Started Electron application {executable} as {adopted['browserId']}")
        if recording["tracing"]:
            trace_file = recording["tracing"]
            logger.info(f"The trace of {adopted['browserId']} is saved to {trace_file} when the application closes")
        video_path = self.register_adopted_context(adopted["contextId"], recording, adopted.get("videoPath"))
        return (
            adopted["browserId"],
            adopted["contextId"],
            NewPageDetails(page_id=adopted.get("pageId", ""), video_path=video_path),
        )

    @keyword
    def close_electron_application(self, browser: SelectionType | str = SelectionType.CURRENT) -> None:
        """Ends an Electron application and removes it from the library state.

        The keyword returns after the application process has exited. It also
        passes if the application has already quit on its own. The browser
        that was active before the application becomes active again.

        *Arguments:*
          - ``browser``: The browser id returned by `New Electron Application`.
                ``CURRENT`` ends the active application, ``ALL`` closes all
                browsers and applications.

        This is the same as `Close Browser` for the application's browser id,
        so `Close Browser`, `Close Context` and automatic closing end
        applications as well.

        Example:
        | ${app}    ${_}    ${_} =    `New Electron Application`    /opt/my-app/my-app
        | `Close Electron Application`    ${app}
        """
        self.close_browser(browser)

    @keyword
    def evaluate_in_main_process(
        self, *function: str, arg: Any = None, browser: SelectionType | str = SelectionType.CURRENT
    ) -> Any:
        """Runs a JavaScript function in the main process of an Electron application and returns its result.

        Browser keywords reach the application's windows, but not its main
        process. There, a test can replace a native dialog before the
        application opens it, size or focus a window, click a menu item, or
        read the application's state. The function runs as with Playwright's
        ``electronApplication.evaluate``.

        *Arguments:*
          - ``function``: A JavaScript function as text. Several arguments are
                joined with line breaks, as for `Evaluate JavaScript`. The
                function gets three parameters: the ``electron`` module,
                ``arg``, and ``window``, the ``BrowserWindow`` that shows the
                active page. For a ``<webview>`` or a ``WebContentsView``, that
                is the window they are shown in. ``window`` is ``null`` if the
                active page is not one of the application's, for example while
                another browser is active. The function may return a promise.
          - ``arg``: A JSON-serialisable value that the function gets.
          - ``browser``: ``CURRENT`` for the active application, or a browser
                id that `New Electron Application` returned.

        *Returns:*
          The function's result, which must be JSON-serialisable. Objects of
          the main process, such as a ``BrowserWindow``, cannot be returned.
          ``None`` if the function returns nothing.

        *Raises:*
          - ``AssertionError``: The browser is not an application started by
                `New Electron Application`, or the function throws an error.

        Example:
        | ${name} =    `Evaluate In Main Process`    ({ app }) => app.getName()
        | `Evaluate In Main Process`    ({ dialog }, path) => {
        | ...        dialog.showOpenDialog = async () => ({ canceled: false, filePaths: [path] });
        | ...    }
        | ...    arg=${EXECDIR}/data/report.csv
        | `Evaluate In Main Process`    (electron, size, window) => window.setBounds(size)
        | ...    arg=${{ {"width": 1280, "height": 720} }}
        """
        if SelectionType.create(browser) is SelectionType.CURRENT:
            active = self.get_browser_ids(SelectionType.CURRENT)
            browser_id = active[0] if active else "CURRENT"
        else:
            browser_id = str(browser)
        self._load_electron_extension()
        return self.call_js_keyword(
            "robotframeworkElectronEvaluate", browserId=browser_id, script="\n".join(function), arg=arg
        )

    def _load_electron_extension(self) -> None:
        if not self._electron_extension_loaded:
            self.init_js_extension(_JS_MODULE)
            self._electron_extension_loaded = True


Electron.__doc__ = cleandoc(_INTRO) + "\n\n" + browser_sections()

__all__ = ["Electron"]
