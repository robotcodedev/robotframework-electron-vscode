"""Documentation that the Electron and VSCode libraries share, with links to the Browser library's documentation."""

from inspect import cleandoc
from urllib.parse import quote

_BROWSER_DOCUMENTATION = "https://marketsquare.github.io/robotframework-browser/Browser.html"


def browser_link(section: str) -> str:
    """Return a Libdoc link to a section of the Browser library's documentation."""
    return f"[{_BROWSER_DOCUMENTATION}#{quote(section)}|{section}]"


def _comparison(start: str, close: str) -> str:
    """Return the table that compares the Browser keywords a library hides with what it offers instead."""
    rows = [
        ("``New Browser``, ``New Persistent Context``, ``Open Browser``", start, "A test starts an application."),
        ("``Close Browser``, ``Close Context``", close, "The application ends with its only context."),
        ("``Switch Browser``", "`Switch Electron Application`", "Several applications can be open at once."),
        ("``Get Browser Ids``", "`Get Electron Application Ids`", "It returns the ids of the open applications."),
        ("``Get Browser Catalog``", "`Get Electron Application Catalog`", "It leaves out the context level."),
        ("``New Context``, ``Switch Context``, ``Get Context Ids``", "-", "An application has exactly one context."),
        ("``New Page``", "-", "The application opens its windows itself."),
        ("``Launch Browser Server``, ``Close Browser Server``, ``Connect To Browser``", "-", "For browsers only."),
        ("``Get Device``, ``Get Devices``", "-", "Devices are options for ``New Context``."),
        ("``Crawl Site``", "-", "It opens pages of its own."),
        ("``Set Storage State``", "-", "It needs a page of its own to write the storage."),
        ("``Tap``", "-", "Touch input is not enabled for applications."),
        ("``Save Page As Pdf``", "-", "Electron does not provide Chromium's PDF printing over the DevTools protocol."),
    ]
    lines = ["| =Browser keyword= | =Here= | =Why= |"]
    lines += [f"| {browser} | {here} | {why} |" for browser, here, why in rows]
    return "\n        ".join(lines)


def _window_forms() -> str:
    """Return the table of the forms in which the window keywords take a window."""
    rows = [
        ("``title=<title>``", "The window that shows this title, exactly as `Get Window Titles` returns it."),
        (
            "``title=/<pattern>/<flags>``",
            (
                "The window whose title matches this JavaScript regular expression, in the form of Browser's "
                "``text=`` selector, for example ``title=/^Settings/i``."
            ),
        ),
        (
            "``window=<n>``",
            (
                "The window with this id from `Get Window Ids`. The bare number works as well, because Robot "
                "Framework reads ``window=2`` as the named argument ``window`` with the value ``2``."
            ),
        ),
        (
            "none",
            "The window that shows the active page, which for a ``<webview>`` or ``WebContentsView`` is around it.",
        ),
    ]
    lines = ["| =Form= | =Window= |"]
    lines += [f"| {form} | {window} |" for form, window in rows]
    return "\n        ".join(lines)


def shared_sections(start: str, close: str) -> str:
    """Return the sections that both libraries share, for a library with the keywords ``start`` and ``close``.

    Browser's keyword documentation links to most of these sections by name, so they keep Browser's names;
    the window keywords link to "Windows and pages". ``start`` and ``close`` are the keywords that start and end
    an application, as links.
    """
    return cleandoc(f"""
        = Browser, Context and Page =

        The Browser library organises web pages in browsers, contexts and
        pages, see {browser_link("Browser, Context and Page")} in its
        documentation. An application maps onto them as follows:

        - An application is a browser of its own with exactly one context. The
          id that {start} returns is the application id.
        - Each window of the application is a page, and so is each
          ``<webview>`` and ``WebContentsView``. `Switch Page` and
          `Get Page Ids` work on all of them, `Get Window Ids` lists only the
          windows, see `Windows and pages`. `Close Page` closes windows and
          the pages of a ``WebContentsView``. On the page of a ``<webview>``,
          it waits forever, so a test removes the ``<webview>`` element from
          its page instead.

        == Compared with the Browser library ==

        The library hides the Browser keywords for browsers and contexts, and
        those that cannot work on an application:

        {_comparison(start, close)}

        A test that needs a web browser as well imports the Browser library
        beside this one and calls the keywords that both libraries have with
        the library name, for example ``Browser.New Page``.

        = Windows and pages =

        Each window of an application is a page, and so is each
        ``<webview>`` and ``WebContentsView`` that it shows. After {start},
        the first window is the active page. `Switch Window` makes the page of
        another window the active page, best by the window's title, because it
        waits until a window shows it. `Get Electron Application Catalog`
        lists all pages with their titles, and `Switch Page` selects any of
        them, also a ``<webview>`` or ``WebContentsView``.

        `Get Window Ids` and `Get Window Titles` list only the windows. The
        keywords that act on a window take it in one of these forms:

        {_window_forms()}

        For a title or an expression, the keywords wait up to the library
        timeout until exactly one window matches, so a test can name a window
        that is still opening. Window ids are valid while the application runs
        and unique only within it, so get them again after
        `Switch Electron Application`.

        = Finding elements =

        Selectors work as in the Browser library, see
        {browser_link("Finding elements")} in its documentation. In an
        application:

        - CSS, ``id=`` and ``text=`` find elements in open shadow roots, and
          ``>>>`` reaches into iframes.
        - ``>>>`` does not reach into a ``<webview>``, which is not an iframe.
          Switch to the page of the ``<webview>`` instead.

        = Assertions =

        Keywords such as `Get Text` take an assertion operator and an expected
        value, and retry until the assertion holds or the timeout has passed,
        see {browser_link("Assertions")} in the Browser library's
        documentation.

        = Implicit waiting =

        Browser keywords wait until their elements are ready, see
        {browser_link("Implicit waiting")} in the Browser library's
        documentation. `Set Browser Timeout` changes how long.

        = Scope Setting =

        Keywords that change a setting, such as `Set Browser Timeout`, take a
        scope that says how long the setting lasts, see
        {browser_link("Scope Setting")} in the Browser library's documentation.

        = Automatic page and context closing =

        An application ends with the test or suite that started it, as the
        Browser library closes browsers and contexts, see
        {browser_link("Automatic page and context closing")} in its
        documentation. {close} ends it earlier.
        """)


def importing(library: str) -> str:
    """Return the import documentation of ``library``, which takes the Browser library's import arguments."""
    return cleandoc(f"""
        {library} library takes the same import arguments as the Browser
        library, described under {browser_link("Importing")} in its
        documentation.

        They configure the Browser keywords, for example their timeout or
        presenter mode, and apply to the windows of applications as to any
        other page. Arguments that are about browsers, such as
        ``external_browser_executable``, have no effect on applications. All
        arguments are named arguments.

        Example:
        | Library    {library}    timeout=20s    enable_presenter_mode=True
        """)


# Notes for Browser keywords that behave differently in applications, by method name. The acceptance
# tests in atest/browser_keywords check what they say.
KEYWORD_NOTES = {
    "close_page": """
        Closes windows and the pages of a ``WebContentsView``. On the page of a
        ``<webview>``, it waits forever: Electron destroys the contents of the
        ``<webview>``, but Chromium reports the page as closed only once the
        ``<webview>`` element is gone. Remove the element instead:

        | `Evaluate JavaScript`    id=guest    (element) => element.remove()

        An application has exactly one context, and ``browser`` takes an
        application id, see `Browser, Context and Page`.
        """,
    "switch_page": """
        Each window of an application is a page, and so are the
        ``<webview>`` and ``WebContentsView`` elements it shows. ``NEW`` takes
        the newest page if it is newer than the active page, which can be a
        ``<webview>`` that loaded after a new window. `Switch Window` switches
        to a window by its title instead. Select a ``<webview>`` or
        ``WebContentsView`` by its page id, which
        `Get Electron Application Catalog` returns with its title. ``browser``
        takes an application id.
        """,
    "get_page_ids": """
        The ids are those of the windows of an application and of the
        ``<webview>`` and ``WebContentsView`` elements they show.
        `Get Electron Application Catalog` returns them with their titles, and
        `Get Window Ids` returns only the windows.
        """,
    "get_viewport_size": """
        Returns ``None`` for the window of an application, which has no
        emulated viewport. `Get Window Size` returns the size that the
        window's page has.
        """,
    "save_storage_state": """
        Fails with ``Target.createTarget: Not supported`` when an http or https
        origin that the application has visited is no longer open in a window:
        Playwright then opens a page of its own, which Electron does not allow.
        The local storage of ``file://`` pages is not saved.
        """,
    "handle_future_dialogs": """
        Electron does not implement ``prompt()``: a page's call fails with
        ``prompt() is not supported.``, so ``prompt_input`` never applies.
        Native dialogs of the main process are not dialogs of the page; replace
        them with `Evaluate In Main Process`.
        """,
    "press_keys": """
        The keys reach the page, but not the accelerators of the application's
        menu. Click a menu item in the main process instead:

        | `Evaluate In Main Process`    ({ Menu }) => Menu.getApplicationMenu().getMenuItemById('open-file').click()
        """,
    "keyboard_key": """
        The keys reach the page, but not the accelerators of the application's
        menu. Click a menu item in the main process instead, see
        `Evaluate In Main Process`.
        """,
}


def with_note(method_name: str, documentation: str) -> str:
    """Return the documentation of a Browser keyword, with the note on applications if it has one."""
    note = KEYWORD_NOTES.get(method_name)
    if note is None:
        return documentation
    return f"{documentation}\n\n*In Electron applications:*\n\n{cleandoc(note)}"
