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
from Browser.utils.data_types import NewPageDetails, RecordHar, SelectionType, ViewportDimensions
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

    | =Key= | =Description= |
    | ``duration`` | How long each action is shown, in milliseconds. |
    | ``position`` | Where the overlay is shown: ``top-left``, ``top``, ``top-right``, ``bottom-left``, ``bottom`` or ``bottom-right``. |
    | ``fontSize`` | Font size of the overlay, in pixels. |
    | ``cursor`` | ``pointer`` shows the mouse cursor, ``none`` hides it. |
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

    | =Key= | =Description= |
    | ``dir`` | Folder for the videos. Relative paths are relative to Browser's video folder ``browser/video`` in the output directory, which is also the default. |
    | ``size`` | Size of the video, as a dictionary with ``width`` and ``height``. Defaults to 1280×720. A larger window is scaled down to fit, a smaller one is shown at its own size with a grey margin. |
    | ``showActions`` | Shows the performed actions in the video: a dictionary with ``duration`` (milliseconds), ``position``, ``fontSize`` and ``cursor``. |

    Example:
    | `New Electron Application`    ${ELECTRON}    record_video={'size': {'width': 1920, 'height': 1080}}
    | `New Electron Application`    ${ELECTRON}    record_video={'showActions': {'duration': 800, 'position': 'top-right'}}
    """

    dir: str
    size: ViewportDimensions
    showActions: ShowActions


class Electron(Browser):
    ROBOT_LIBRARY_VERSION = __version__

    _electron_extension_loaded = False

    # The signature and the types of the import arguments come from Browser through __wrapped__.
    @functools.wraps(Browser.__init__)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

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
    ) -> tuple[str, str, NewPageDetails]:
        """Starts an Electron application and makes its first window the active page.

        The application becomes a new active browser with one context. Its
        windows are pages of that context, so Browser keywords like `Click`
        and `Get Text` work on them, and windows the application opens later
        can be selected with `Switch Page`. `Close Electron Application`,
        `Close Browser` and automatic closing end the application.

        *Arguments:*
          - ``executable_path``: The Electron executable, as a path or as a
                command found on ``PATH``. For an app that is run by the plain
                Electron binary, pass the app folder in ``args``.
          - ``args``: Command-line arguments for the application.
          - ``env``: Environment variables of the application. If not given,
                the application gets the environment of the test run without
                ``ELECTRON_RUN_AS_NODE``, which runs started from VS Code have
                and which would make Electron run as plain Node.js.
          - ``cwd``: Working directory of the application.
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

        *Returns:*
          A tuple of browser id, context id and page details of the first
          window, like `New Persistent Context`. The page details contain the
          path of the video, or an empty string if no video is recorded.

        *Raises:*
          - ``ValueError``: The executable is not found, or ``record_har`` has
                no ``path``.

        Example:
        | ${app} =    `New Electron Application`    /opt/my-app/my-app
        | `Get Title`    ==    My App
        | `New Electron Application`    ${ELECTRON}    args=${{ [$EXECDIR + "/app"] }}
        | `New Electron Application`    /opt/my-app/my-app    tracing=True    record_har={'path': 'my-app.har'}
        """
        executable = shutil.which(str(executable_path))
        if executable is None:
            raise ValueError(f"Electron executable '{executable_path}' not found.")
        if env is None:
            env = {k: v for k, v in os.environ.items() if k != "ELECTRON_RUN_AS_NODE"}
        if not self._electron_extension_loaded:
            self.init_js_extension(_JS_MODULE)
            self._electron_extension_loaded = True
        video = self._video_options(record_video)
        trace_file = self._playwright_state._resolve_trace_file(tracing)
        adopted = self.call_js_keyword(
            "robotframeworkElectronLaunch",
            executablePath=executable,
            args=args or [],
            env=env,
            cwd=str(cwd) if cwd else None,
            timeout=self.get_timeout(timeout),
            recordVideo=video,
            recordHar=self._har_options(record_har),
            tracing=trace_file or None,
        )
        logger.info(f"Started Electron application {executable} as {adopted['browserId']}")
        if trace_file:
            logger.info(f"The trace of {adopted['browserId']} is saved to {trace_file} when the application closes")
            self._playwright_state.add_context_and_keyword_call_stack_to_trace(trace_file, adopted["contextId"])
        if video is not None:
            self._playwright_state.context_cache.add(adopted["contextId"], video["size"])
        video_path = self._playwright_state._embed_video(
            {"video_path": adopted.get("videoPath"), "contextUuid": adopted["contextId"]}
        )
        return (
            adopted["browserId"],
            adopted["contextId"],
            NewPageDetails(page_id=adopted["pageId"], video_path=video_path),
        )

    def _video_options(self, record_video: RecordVideo | None) -> dict[str, Any] | None:
        """Resolve folder and size of ``record_video`` the way Browser does for ``recordVideo``."""
        if record_video is None:
            return None
        state = self._playwright_state
        params = state._set_video_size_to_int(state._set_video_path({"recordVideo": {"dir": None, **record_video}}))
        return {**params["recordVideo"], "dir": str(params["recordVideo"]["dir"])}

    def _har_options(self, record_har: RecordHar | None) -> dict[str, Any] | None:
        """Resolve a relative HAR path against the output directory."""
        if record_har is None:
            return None
        if "path" not in record_har:
            raise ValueError("record_har needs a 'path' for the HAR file.")
        return {**record_har, "path": str(Path(self.outputdir, record_har["path"]))}

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


Electron.__doc__ = cleandoc(_INTRO) + "\n\n" + browser_sections()

__all__ = ["Electron"]
