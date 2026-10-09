"""Robot Framework library for testing Electron applications, built on the Browser library."""

import os
import shutil
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any, TypedDict

from Browser import Browser
from Browser.utils import logger
from Browser.utils.data_types import NewPageDetails, SelectionType, ViewportDimensions
from robotlibcore import keyword

__version__ = version("robotframework-electron")

_JS_MODULE = Path(__file__).with_name("electron.js")

_INTRO = """
Electron library is a Robot Framework library for testing Electron applications.

It is built on the [https://robotframework-browser.org|Browser library]: it
contains every Browser keyword and takes the same import arguments. Import
``Electron`` instead of ``Browser``, start an application with
`New Electron Application`, and use Browser keywords such as `Click` and
`Get Text` on its windows. Each application window is a page of the
application's context.

= Browser library documentation =

The rest of this documentation is the Browser library's own.
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

    @keyword
    def new_electron_application(
        self,
        executable_path: Path,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
        timeout: timedelta | None = None,
        record_video: RecordVideo | None = None,
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

        Returns a tuple of browser id, context id and page details of the
        first window, like `New Persistent Context`. The page details contain
        the path of the video, or an empty string if no video is recorded.

        Example:
        | ${app} =    `New Electron Application`    /opt/my-app/my-app
        | `Get Title`    ==    My App
        | `New Electron Application`    ${ELECTRON}    args=${{ [$EXECDIR + "/app"] }}
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
        adopted = self.call_js_keyword(
            "robotframeworkElectronLaunch",
            executablePath=executable,
            args=args or [],
            env=env,
            cwd=str(cwd) if cwd else None,
            timeout=self.get_timeout(timeout),
            recordVideo=video,
        )
        logger.info(f"Started Electron application {executable} as {adopted['browserId']}")
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


Electron.__doc__ = cleandoc(_INTRO) + "\n\n" + cleandoc(Browser.__doc__ or "")

__all__ = ["Electron"]
