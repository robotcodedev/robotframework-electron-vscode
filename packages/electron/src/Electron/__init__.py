"""Robot Framework library for testing Electron applications, built on the Browser library."""

import functools
import os
import shutil
import time
from datetime import timedelta
from importlib.metadata import version
from inspect import cleandoc
from pathlib import Path
from typing import Any

from assertionengine import AssertionOperator, float_str_verify_assertion, int_dict_verify_assertion, verify_assertion
from Browser import Browser
from Browser.assertion_engine import with_assertion_polling
from Browser.utils import logger
from Browser.utils.data_types import ColorScheme, NewPageDetails, RecordHar, RecordVideo, SelectionType, SizeFields
from robot.utils import DotDict
from robotlibcore import keyword

from ._docs import importing, shared_sections, with_note

__version__ = version("robotframework-electron")

_JS_MODULE = Path(__file__).with_name("electron.js")

_INTRO = """
Electron library is a Robot Framework library for testing Electron applications.

It is built on the [https://robotframework-browser.org|Browser library]: its
keywords, such as `Click` and `Get Text`, act on the windows of an application.
Import ``Electron`` instead of ``Browser``. The library hides Browser's keywords
for browsers and contexts, see `Browser, Context and Page`. Guides and examples
are on the
[https://robotcodedev.github.io/robotframework-electron-vscode/|documentation site].

= Starting and closing an application =

`Start Electron Application` starts an application and waits for its first
window. Pass the application's executable, or for an application that the plain
Electron binary runs, the Electron executable and the application folder in
``args``. The library downloads nothing: the npm package ``electron``, for
example, brings an Electron release, and ``require('electron')`` returns its
executable.

| ${app}    ${page} =    `Start Electron Application`    /opt/my-app/my-app
| `Get Title`    ==    My App
| `Click`    text=Settings

`Close Electron Application` ends an application. Automatic closing ends it with
the test or suite that started it, see `Automatic page and context closing`.

Each window of an application is a page for Browser keywords, see
`Windows and pages`.

= Several applications =

Several applications can be open at once. `Switch Electron Application` makes
another one the active application, and `Get Electron Application Ids` returns
their ids.

= The main process =

Browser keywords reach the windows, but not the application's main process.
`Evaluate In Main Process` runs a JavaScript function there, for example to
replace a native dialog or click a menu item. `Set Window Size`,
`Maximize Window` and the other window keywords size windows and change their
state, see `Windows and pages`.

= Launch options =

`Start Electron Application` takes some options of the Browser library's
``New Context``: ``color_scheme``, ``locale``, ``timezone_id`` and
``bypass_csp``. They apply from the start, so another value means starting the
application again.

= Videos, traces and HAR files =

`Start Electron Application` records a video of the windows with
``record_video``, a Playwright trace with ``tracing``, and the network traffic
of the windows with ``record_har``. They are saved when the application closes.
"""


# Browser keywords that the library does not offer, by method name. An application is one
# browser with one context: these keywords create, switch, list or close browsers and
# contexts, or they fail on an application. Browser's own code still calls the methods.
HIDDEN_KEYWORDS = frozenset(
    {
        "new_browser",
        "open_browser",
        "close_browser",
        "switch_browser",
        "get_browser_ids",
        "get_browser_catalog",
        "launch_browser_server",
        "close_browser_server",
        "connect_to_browser",
        "new_context",
        "new_persistent_context",
        "close_context",
        "switch_context",
        "get_context_ids",
        "new_page",
        "get_device",
        "get_devices",
        "crawl_site",
        "set_storage_state",
        "tap",
        "save_page_as_pdf",
    }
)


class Electron(Browser):
    ROBOT_LIBRARY_VERSION = __version__

    _electron_extension_loaded = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    # Libdoc and robotlibcore take the signature and the types of the import arguments
    # from Browser through __wrapped__. A decorator would hide __init__ from mypy.
    functools.update_wrapper(__init__, Browser.__init__)
    __init__.__doc__ = importing("Electron")

    def get_keyword_names(self) -> list[str]:
        """Returns the keyword names without those of ``HIDDEN_KEYWORDS``.

        The keywords are compared by their method, so that translated names are hidden as well.
        """
        names: list[str] = super().get_keyword_names()
        return [name for name in names if self.keywords[name].__name__ not in HIDDEN_KEYWORDS]

    def get_keyword_documentation(self, name: str) -> str:
        """Returns Browser's documentation, with a note for Browser keywords that behave differently in applications."""
        documentation: str = super().get_keyword_documentation(name)  # type: ignore[no-untyped-call]
        method = self.keywords.get(name)
        return with_note(method.__name__, documentation) if method is not None else documentation

    @keyword
    def start_electron_application(
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
    ) -> tuple[str, NewPageDetails]:
        """Starts an Electron application and makes its first window the active page.

        The application becomes the active application. Its windows are
        pages, so Browser keywords like `Click` and `Get Text` work on them,
        and windows the application opens later can be selected with
        `Switch Window`. `Close Electron Application` and automatic closing end
        the application.

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
                see `RecordVideo` for the folder, size, frame rate and the
                annotations of the performed actions. An empty dictionary
                records with the defaults: Browser's video folder
                ``browser/video`` in the output directory and a size of
                1280x720. A larger window is scaled down to fit, a smaller one
                is shown at its own size with a grey margin. The log embeds the
                video, and the file is complete once the application has
                closed. Recording needs Playwright's ffmpeg, which is installed
                with Browser's browsers.
          - ``record_har``: Records the network traffic of the application's
                windows into a [http://www.softwareishard.com/blog/har-12-spec/|HAR]
                file, as ``recordHar`` of the Browser library's ``New Context``: a dictionary with the
                ``path`` of the file and optionally ``omitContent``. A relative
                path is relative to the output directory. The file is written
                when the application closes.
          - ``tracing``: Records a Playwright trace of the application, as
                ``tracing`` of the Browser library's ``New Context``: ``True`` saves it in
                ``browser/traces`` in the output directory, named after the
                application's context, and a ``*.zip`` path or a folder saves it
                there. Give a path to know the file's name. The variable or
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
                windows, including Trusted Types, as ``bypassCSP`` of the
                Browser library's ``New Context``. Features that add scripts to a page need it in
                applications with a strict policy, for example `Record Selector`
                in VS Code. It also applies to webviews and frames, so that
                policy problems of the application go unnoticed. Switch it on
                only where a feature needs it.

        *Returns:*
          A tuple of the application id and the page details of the first
          window. The page details contain the page id and the path of the
          video, or an empty string if no video is recorded.

        *Raises:*
          - ``ValueError``: The executable is not found.

        Example:
        | ${app}    ${page} =    `Start Electron Application`    /opt/my-app/my-app
        | `Get Title`    ==    My App
        | `Start Electron Application`    ${ELECTRON}    args=${{ [$EXECDIR + "/app"] }}
        | `Start Electron Application`    /opt/my-app/my-app    tracing=True    record_har={'path': 'my-app.har'}
        | `Start Electron Application`    /opt/my-app/my-app    color_scheme=dark    locale=de-DE
        | `Start Electron Application`    /opt/my-app/my-app    record_video={'showActions': {'position': 'bottom'}}
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
        )
        logger.info(f"Started Electron application {executable} as {adopted['browserId']}")
        if recording["tracing"]:
            trace_file = recording["tracing"]
            logger.info(f"The trace of {adopted['browserId']} is saved to {trace_file} when the application closes")
        page_details = NewPageDetails(page_id=adopted.get("pageId", ""), video_path=adopted.get("videoPath") or "")
        return adopted["browserId"], page_details

    @keyword
    def close_electron_application(self, application: SelectionType | str = SelectionType.CURRENT) -> None:
        """Ends an Electron application and removes it from the library state.

        The keyword returns after the application process has exited. It also
        passes if the application has already quit on its own. The application
        that was active before becomes active again. Automatic closing ends
        applications as well, see `Automatic page and context closing`.

        *Arguments:*
          - ``application``: The application id that `Start Electron Application`
                returned. ``CURRENT`` ends the active application, ``ALL`` ends
                all applications.

        Example:
        | ${app}    ${_} =    `Start Electron Application`    /opt/my-app/my-app
        | `Close Electron Application`    ${app}
        | `Close Electron Application`    ALL
        """
        self.close_browser(application)

    @keyword
    def switch_electron_application(self, application: str) -> str:
        """Makes another open application the active one.

        Browser keywords then act on the active page of that application.

        *Arguments:*
          - ``application``: The application id that `Start Electron Application`
                returned.

        *Returns:*
          The id of the application that was active before.

        Example:
        | ${first}    ${_} =    `Start Electron Application`    /opt/my-app/my-app
        | `Start Electron Application`    /opt/other-app/other-app
        | `Switch Electron Application`    ${first}
        """
        previous: str = self.switch_browser(application)
        return previous

    @keyword
    def get_electron_application_ids(self, selection: SelectionType = SelectionType.ALL) -> list[str]:
        """Returns the ids of the open applications.

        *Arguments:*
          - ``selection``: ``ALL`` for all open applications, ``ACTIVE`` or
                ``CURRENT`` for the active one.

        *Returns:*
          A list of application ids, as `Start Electron Application` returned them.

        Example:
        | ${ids} =    `Get Electron Application Ids`
        | ${active} =    `Get Electron Application Ids`    ACTIVE
        """
        ids: list[str] = self.get_browser_ids(selection)
        return ids

    @keyword
    def get_electron_application_catalog(self) -> list[dict[str, Any]]:
        """Returns the open applications with their pages.

        Every window, ``<webview>`` and ``WebContentsView`` of an application
        is a page. The catalog helps to find the page id of one of them for
        `Switch Page`.

        *Returns:*
          A list with one dictionary per application: its ``id``, whether it
          is the ``active`` application, and its ``pages``. Each page has its
          ``id``, ``title``, ``url``, and whether it is the ``active`` page of
          its application.

        Example:
        | ${catalog} =    `Get Electron Application Catalog`
        | FOR    ${page}    IN    @{catalog}[0][pages]
        |     Log    ${page}[title]: ${page}[id]
        | END
        """
        catalog = []
        for browser in self.get_browser_catalog():
            # An application has one context; Browser's catalog lists it as a level of its own.
            pages = [
                {
                    "id": page["id"],
                    "title": page["title"],
                    "url": page["url"],
                    "active": page["id"] == context.get("activePage"),
                }
                for context in browser.get("contexts", [])
                for page in context.get("pages", [])
            ]
            catalog.append({"id": browser["id"], "active": browser.get("activeBrowser", False), "pages": pages})
        return catalog

    @keyword
    def evaluate_in_main_process(
        self, function: str, *lines: str, arg: Any = None, application: SelectionType | str = SelectionType.CURRENT
    ) -> Any:
        """Runs a JavaScript function in the main process of an Electron application and returns its result.

        Browser keywords reach the application's windows, but not its main
        process. There, a test can replace a native dialog before the
        application opens it, focus a window, click a menu item, or read the
        application's state. The window keywords, such as `Set Window Size`
        and `Maximize Window`, size windows and change their state. The
        function runs as with Playwright's ``electronApplication.evaluate``.

        *Arguments:*
          - ``function``: A JavaScript function as text, or its first line.
                The function gets three parameters: the ``electron`` module,
                ``arg``, and ``window``, the ``BrowserWindow`` that shows the
                active page. For a ``<webview>`` or a ``WebContentsView``, that
                is the window they are shown in. ``window`` is ``null`` if the
                active page is not one of the application's, for example while
                another application is active. The function may return a promise.
          - ``lines``: Further lines of the function. They are joined to
                ``function`` with line breaks, so that a function can span
                several cells with ``...``.
          - ``arg``: A JSON-serialisable value that the function gets.
          - ``application``: ``CURRENT`` for the active application, or an
                application id that `Start Electron Application` returned.

        *Returns:*
          The function's result, which must be JSON-serialisable. Objects of
          the main process, such as a ``BrowserWindow``, cannot be returned.
          ``None`` if the function returns nothing.

        *Raises:*
          - ``AssertionError``: No application is open, the id is not an
                application started by `Start Electron Application`, or the
                function throws an error.

        Example:
        | ${name} =    `Evaluate In Main Process`    ({ app }) => app.getName()
        | `Evaluate In Main Process`    ({ dialog }, path) => {
        | ...        dialog.showOpenDialog = async () => ({ canceled: false, filePaths: [path] });
        | ...    }
        | ...    arg=${EXECDIR}/data/report.csv
        | ${focused} =    `Evaluate In Main Process`    (electron, arg, window) => window.isFocused()
        """
        if SelectionType.create(application) is SelectionType.CURRENT:
            browser_id = self._active_application()
        else:
            browser_id = str(application)
        self._load_electron_extension()
        script = "\n".join((function, *lines))
        return self.call_js_keyword("robotframeworkElectronEvaluate", browserId=browser_id, script=script, arg=arg)

    @keyword
    def get_window_ids(self, selection: SelectionType = SelectionType.ALL) -> list[str]:
        """Returns the ids of the active application's windows.

        The windows are the application's ``BrowserWindow`` objects. A
        ``<webview>`` or ``WebContentsView`` is a page, but no window, see
        `Windows and pages`. The ids are valid while the application runs.

        *Arguments:*
          - ``selection``: ``ALL`` for all windows, in the order in which they
                opened, ``ACTIVE`` or ``CURRENT`` for the window that shows the
                active page.

        *Returns:*
          A list of window ids such as ``window=1``, which the window keywords
          take, for example `Maximize Window` and `Switch Window`.

        Example:
        | ${windows} =    `Get Window Ids`
        | `Maximize Window`    ${windows}[1]
        | ${active} =    `Get Window Ids`    ACTIVE
        """
        windows = self._windows(active=SelectionType.create(selection) is SelectionType.CURRENT)
        return [f"window={window['id']}" for window in windows]

    @keyword
    def get_window_titles(self) -> list[str]:
        """Returns the titles that the active application's windows show.

        The titles are in the order of `Get Window Ids`. A window shows the
        title of its page, unless the application gives it one of its own.
        The window keywords take a window by its title, see
        `Windows and pages`.

        Example:
        | ${titles} =    `Get Window Titles`
        | Should Contain    ${titles}    Settings
        | `Switch Window`    title=Settings
        """
        return [window["title"] for window in self._windows(active=False)]

    @keyword
    def set_window_size(self, width: int, height: int, window: str | None = None) -> None:
        """Gives a window the content size ``width`` x ``height`` and waits until it has it.

        The content size is the area that the window's page shows, which its
        screenshots and its video have as well. A maximised, minimised or
        fullscreen window is made normal first. At a fractional display scale,
        the size can be off by up to 2 pixels, because the window's edges snap
        to whole device pixels.

        *Arguments:*
          - ``width``: The width of the content in pixels.
          - ``height``: The height of the content in pixels.
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page.

        *Raises:*
          - ``AssertionError``: The window does not get the size within the
                library timeout, for example because the screen is smaller.
                The error names the size that the window has.

        Example:
        | `Set Window Size`    1280    720
        | `Set Window Size`    1024    700    title=Settings
        """
        self._adjust_window(window, "normal", {"width": width, "height": height})

    @keyword
    @with_assertion_polling
    def get_window_size(
        self,
        key: SizeFields = SizeFields.ALL,
        assertion_operator: AssertionOperator | None = None,
        assertion_expected: Any | None = None,
        message: str | None = None,
        window: str | None = None,
    ) -> Any:
        """Returns the content size of a window.

        The content size is the area that the window's page shows, see
        `Set Window Size`. Browser's `Get Viewport Size` returns ``None`` for
        an application's window, which has no emulated viewport.

        *Arguments:*
          - ``key``: ``ALL`` returns a dictionary with ``width`` and
                ``height``, ``width`` or ``height`` only that value.
          - ``assertion_operator``: See `Assertions`.
          - ``assertion_expected``: The expected value of the assertion.
          - ``message``: Overrides the default error message of the assertion.
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page. After the assertion
                arguments, it is given by name.

        Example:
        | ${size} =    `Get Window Size`
        | `Get Window Size`    width    ==    1280
        | `Get Window Size`    ALL    ==    {'width': 1024, 'height': 700}    window=title=Settings
        """
        state = self._window_state(window)
        size = DotDict(width=state["width"], height=state["height"])
        if key == SizeFields.ALL:
            return int_dict_verify_assertion(size, assertion_operator, assertion_expected, "Window size is", message)
        return float_str_verify_assertion(
            size[key.name], assertion_operator, assertion_expected, f"Window {key.name} is", message
        )

    @keyword
    def maximize_window(self, window: str | None = None) -> None:
        """Maximises a window and waits until it is maximised.

        A fullscreen window leaves fullscreen first. Maximising needs a window
        manager. On a display without one, for example plain Xvfb, the
        keyword fails after the library timeout.

        *Arguments:*
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page.

        Example:
        | `Maximize Window`
        | `Maximize Window`    title=Settings
        """
        self._adjust_window(window, "maximized")

    @keyword
    def minimize_window(self, window: str | None = None) -> None:
        """Minimises a window and waits until it is minimised.

        A minimised window draws nothing, so Browser keywords on its page wait
        until their timeout. `Restore Window` brings it back. A fullscreen
        window leaves fullscreen first. Minimising needs a window manager, and
        some desktops cannot minimise windows, for example niri. There, the
        keyword fails after the library timeout.

        *Arguments:*
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page.

        Example:
        | `Minimize Window`
        | `Restore Window`
        """
        self._adjust_window(window, "minimized")

    @keyword
    def restore_window(self, window: str | None = None) -> None:
        """Brings a maximised, minimised or fullscreen window back to its normal state and waits until it is there.

        A window that was maximised before it was minimised is normal
        afterwards as well.

        *Arguments:*
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page.

        Example:
        | `Maximize Window`
        | `Restore Window`
        | `Get Window State`    ==    normal
        """
        self._adjust_window(window, "normal")

    @keyword
    @with_assertion_polling
    def get_window_state(
        self,
        assertion_operator: AssertionOperator | None = None,
        assertion_expected: Any | None = None,
        message: str | None = None,
        window: str | None = None,
    ) -> Any:
        """Returns the state of a window: ``normal``, ``maximized`` or ``minimized``.

        A fullscreen window, which fills the screen, counts as ``maximized``.

        *Arguments:*
          - ``assertion_operator``: See `Assertions`.
          - ``assertion_expected``: The expected value of the assertion.
          - ``message``: Overrides the default error message of the assertion.
          - ``window``: The window, see `Windows and pages`. Defaults to the
                window that shows the active page. After the assertion
                arguments, it is given by name.

        Example:
        | `Get Window State`    ==    maximized
        | ${state} =    `Get Window State`    window=title=Settings
        """
        state = self._window_state(window)["state"]
        return verify_assertion(state, assertion_operator, assertion_expected, "Window state", message)

    @keyword
    def switch_window(self, window: str) -> str:
        """Makes the own page of a window the active page and returns the id of the page that was active before.

        Browser keywords then act on that page, and the window comes to the
        front. `Switch Page` does the same for any page; `Switch Window`
        switches only to windows and fails instead of switching to a
        ``<webview>`` or ``WebContentsView``.

        *Arguments:*
          - ``window``: The window, as ``title=<title>``, as a regular
                expression ``title=/<pattern>/<flags>`` or as an id from
                `Get Window Ids`, see `Windows and pages`, or the page id of
                its page, as `Switch Page` takes it, or ``NEW`` for the newest
                page. A title suits a window that the application opens best,
                because the keyword waits until the window shows it. ``NEW``
                takes the newest page if it is newer than the active page, as
                `Switch Page` does: that can be a ``<webview>`` that loaded after
                the window, or after a switch back to an older window, a page
                that was open before.

        *Returns:*
          The id of the page that was active before. `Switch Window` and
          `Switch Page` switch back to it.

        *Raises:*
          - ``AssertionError``: No window matches, or the page is not a
                window's own page. The active page then stays the same. For a
                title, an expression or a window id, the keyword finds the
                window's page in Browser's catalog by the page's title, so the
                page needs a title that no other page of the application has.
                Otherwise, switch with the page id.

        Example:
        | `Click`    text=Settings
        | ${previous} =    `Switch Window`    title=Settings
        | `Click`    text=Save
        | `Switch Window`    ${previous}
        """
        self._active_application()
        new = window.upper() == "NEW"
        if new or window.startswith("page="):
            # Browser's Node side takes NEW in capitals only.
            previous: str = self.switch_page("NEW" if new else window)
            if self._window_of_active_page() is None:
                self.switch_page(previous)
                page = "The newest page" if new else f"The page '{window}'"
                raise AssertionError(
                    f"{page} is not a window, but a <webview> or WebContentsView, which Switch Page selects."
                )
            return previous
        deadline = time.monotonic() + self.timeout / 1000
        found = self._call_in_application("robotframeworkElectronWindowPage", window=window)
        page_id = self._page_of_window(found["id"], found["pageTitle"], deadline)
        previous = self.switch_page(page_id)
        if self._window_of_active_page() != found["id"]:
            self.switch_page(previous)
            raise AssertionError(f"The page '{page_id}' is not the own page of the window 'window={found['id']}'.")
        return previous

    def _page_of_window(self, window_id: int, title: str | None, deadline: float) -> str:
        """Return the id of the own page of the window ``window_id``, found in Browser's catalog by its title.

        ``title`` is the title of the page as electron.js read it. Until ``deadline``, a ``time.monotonic()``
        value, it looks for exactly one page of the active application with that title, and reads the title again
        while there is none: Browser indexes a new page a moment after the page opens, its catalog lists an empty
        title for a page that is too busy to answer in time, and the page can change its title in between.
        """
        window = f"window={window_id}"
        while True:
            matches = [] if title is None else self._pages_with_title(title)
            if len(matches) == 1:
                return matches[0]
            if time.monotonic() >= deadline:
                if title is None:
                    raise AssertionError(
                        f"The page of the window '{window}' has no title, by which Switch Window finds it. "
                        "Switch to the page with its page id."
                    )
                if matches:
                    raise AssertionError(
                        f"The pages {', '.join(matches)} all have the title '{title}' of the page of the window "
                        f"'{window}'. Switch to one of them with its page id."
                    )
                raise AssertionError(f"No page of the application has the title '{title}' of the window '{window}'.")
            time.sleep(0.1)
            found = self._call_in_application("robotframeworkElectronWindowPage", window=window, defaultTimeout=0)
            title = found["pageTitle"]

    def _pages_with_title(self, title: str) -> list[str]:
        application = self._active_application()
        catalog = self.get_electron_application_catalog()
        pages: list[dict[str, Any]] = next((entry["pages"] for entry in catalog if entry["id"] == application), [])
        return [str(page["id"]) for page in pages if page["title"] == title]

    def _window_of_active_page(self) -> int | None:
        """Return the id of the window whose own page the active page is, in the application that is active now.

        Switch Page switches to the application of a page id, so this can be another one than before it.
        """
        window: int | None = self._call_in_application("robotframeworkElectronWindowOfPage")
        return window

    def _adjust_window(self, window: str | None, state: str, size: dict[str, int] | None = None) -> None:
        self._call_in_application("robotframeworkElectronAdjustWindow", window=window, state=state, size=size)

    def _window_state(self, window: str | None) -> dict[str, Any]:
        state: dict[str, Any] = self._call_in_application("robotframeworkElectronGetWindow", window=window)
        return state

    def _windows(self, active: bool) -> list[dict[str, Any]]:
        windows: list[dict[str, Any]] = self._call_in_application("robotframeworkElectronWindows", active=active)
        return windows

    def _call_in_application(self, function: str, **arguments: Any) -> Any:
        """Return the result of the function ``function`` of electron.js for the active application.

        It does not load electron.js: every application comes from `Start Electron Application`, which loads it.
        """
        return self.call_js_keyword(function, browserId=self._active_application(), **arguments)

    def _active_application(self) -> str:
        active = self.get_browser_ids(SelectionType.CURRENT)
        if not active:
            raise AssertionError("No application is open.")
        return str(active[0])

    def _load_electron_extension(self) -> None:
        if not self._electron_extension_loaded:
            self.init_js_extension(_JS_MODULE)
            self._electron_extension_loaded = True


Electron.__doc__ = (
    cleandoc(_INTRO) + "\n\n" + shared_sections("`Start Electron Application`", "`Close Electron Application`")
)

__all__ = ["HIDDEN_KEYWORDS", "Electron"]
