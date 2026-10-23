# Design

## Context

The motivation is in proposal.md, and the behaviour is in the specs. These facts shape the approach. "Measured" means a spike on 2026-10-22 and 2026-10-23 with the fixture app under Xvfb, with and without Openbox, and with VS Code 1.141.

- **Electron reports what the window manager did.** `maximize()`, `minimize()`, `restore()`, `unmaximize()` and `setContentSize()` of a `BrowserWindow` return at once; the window manager applies the change afterwards, or not at all. `isMaximized()`, `isMinimized()` and `getContentSize()` report the applied state. `BrowserWindow.getAllWindows()` lists the windows in no particular order, `BrowserWindow.fromId()` finds one, and Electron numbers the windows upwards in the order they open.
  - Measured with Openbox: every change was applied within about 50 ms. `restore()` brought a window that had been maximised before it was minimised back maximised. The content size was the page's `innerWidth` and `innerHeight`; Browser's `Get Viewport Size` returns `None` for an application's window.
  - Measured without a window manager: maximising and minimising changed nothing, while `setContentSize()` worked.
- **electron.js already finds windows.** `robotframeworkElectronEvaluate` gets the window that shows the active page with Playwright's `browserWindow(page)`, which gives the window around a view or `<webview>`, as measured. `isWindowPage` tells a window's own page from views and `<webview>`s by comparing the page's web contents with the window's. `webContents.getType()` cannot do that: it reports `window` for a `WebContentsView`, as measured.
- **Only Browser knows its page ids.** Browser keeps them in its page stack (`IndexedPage { id, p }`), inside a bundle that exports nothing; an extension gets the Playwright objects without ids. Only `Switch Page` changes the active page, by Browser's id or with `NEW`, and it calls `bringToFront()`, which moved the focus to the page's window, as measured.
- **Titles are known on both sides.** Browser's catalog lists the title of every page with its id; it reads a title with a timeout of 350 ms and lists an empty one for a page that does not answer in time. In the main process, `webContents.getTitle()` gives the title of a window's page, and `getTitle()` the title that the window shows. A window shows its page's title unless the application prevents `page-title-updated` and sets its own. URLs are no help: VS Code's windows share one URL, and a window with a moved editor shows `about:blank`, as measured.
- **`Switch Page    NEW`** takes the newest page if it is newer than the active page. Measured: it landed on the `<webview>` of a new window once the `<webview>` had loaded, and after a switch back to an older window, on a page of a window that was already open.
- **Browser's getters** use `with_assertion_polling`: a failing assertion is retried for `retry_assertions_for`, one second by default, within the library timeout.

## Goals / Non-Goals

**Goals:**
- No change to the Browser library and no new dependency, and nothing that relies on Browser's internals.
- A test gives a window as its user sees it, by its title, and by its id where titles repeat.
- `Get Window Ids`, `Get Window Titles` and the size and state keywords keep the active page, because they work in the main process alone. Only `Switch Window` goes through Browser.

**Non-Goals:**
- Fullscreen, window positions and `Close Window`. They can follow when tests need them.
- Windows of an application that is not the active one. `Switch Electron Application` selects the application first.
- Patterns for titles. Glob patterns failed in the spike: `*readme.md*` matched two VS Code windows, and `[Preview]`, which VS Code puts into titles, is a character class in a glob. Patterns can follow with a syntax of their own.
- Changing what `NEW` selects. It stays Browser's, with a check.
- Maximising by setting the bounds where the window manager does not maximise. The keyword fails instead, so that a test does not pass on a window that only looks maximised.
- A maximised start in the example. It keeps VS Code's setting `window.newWindowDimensions=maximized`, which opens the window maximised before its first frame.

## Decisions

### Window ids are `window=<n>`

A window id is the text `window=` followed by Electron's id of the `BrowserWindow`, for example `window=2`.

- It reads like Browser's ids (`browser=…`, `page=…`), so logs and errors show what kind of id a value is.
- The keywords accept the bare number as well. Their argument for the window is called `window`, and Robot Framework reads a literal `window=2` as that named argument with the value `2`; so both give the same window.
- Plain numbers as the returned ids were the alternative. `${windows}[1]` and the id `1` would be easy to mix up, and numbers invite hard-coded ids, which depend on the order in which an application opens its windows.
- Electron's ids are unique within one application only. The keywords read an id in the active application, as every window keyword acts on it.

### A window is given by its title or its id

The window keywords take a window as `title=<title>` or as an id. The main process finds it, with `getTitle()` over `getAllWindows()` or with `fromId()`.

- **The title** is what a user sees on the desktop and what a test names a window by. SeleniumLibrary selects windows by title as well, and lists them with `Get Window Titles`.
- **Exact titles:** a title matches only as a whole, see the non-goals.
- **Waiting:** for a title, the keywords wait up to the library timeout until exactly one window shows it. A test can so name a window that is still opening, which replaces `NEW` for most tests. Several windows with the title fail at the timeout with an error that names them.
- **An id** either is a window of the active application or fails at once.

### The main process does the window work

`electron.js` gets functions for the window ids, the titles, the size and the state. Each runs one function in the main process with `application.evaluate`, as `Evaluate In Main Process` does.

- **Which window:** the given window, or without one, the window of the active page through `browserWindow(page)`.
- **`Get Window Ids`:** takes `ALL` or `ACTIVE` like `Get Electron Application Ids` and returns a list in both cases. `ALL` is `BrowserWindow.getAllWindows()`, sorted by id, so that the list follows the order in which the windows opened. Hidden windows count, because they are `BrowserWindow`s with pages as well.
- **`Get Window Titles`:** `getTitle()` of the same windows in the same order.
- **No Browser calls:** these keywords never call Browser, so the active page stays as it is.

### Waiting in the main process, by polling

The function that changes a window also waits for the change. It checks the window's state or content size every 50 ms until it matches or the library timeout is over, which `call_js_keyword` passes as `defaultTimeout`.

- **Polling instead of events:** polling checks exactly what `Get Window State` and `Get Window Size` report, and at the timeout it has the actual state for the error. Events would need the same check, because they do not fire when the window manager ignores a request.
- **`Restore Window`:** `restore()` brings a minimised window back to its previous state, which may be maximised; `unmaximize()` then makes it normal.
- **`Set Window Size`:** first makes the window normal as `Restore Window` does, then calls `setContentSize()`. The size must match exactly at a whole display scale, and within 2 pixels at a fractional one, which the main process reads from the window's display.
- **Failures:** if the timeout is over first, `electron.js` throws an error with the requested and the actual state or size and the likely causes. For maximising and minimising, those are a display without a window manager, such as plain Xvfb, and a desktop that cannot do it, such as niri, which cannot minimise windows. For sizes, they are the screen, a tiling window manager, and the window's minimum or maximum size. The library cannot tell which cause applies, so it names them.

### Getters on Browser's assertion engine

`Get Window Size` takes `key`, `assertion_operator`, `assertion_expected` and `message` as `Get Viewport Size` does, with Browser's `SizeFields`, and `Get Window State` takes the last three. Both use Browser's `with_assertion_polling`, so they retry as Browser's getters do.

The window comes after the assertion arguments, so a test passes it by name: `Get Window State    ==    maximized    window=title=Settings`. The keywords that change a window take it as their last argument too, where it can be given by position: `Maximize Window    title=Settings`, `Set Window Size    1024    700    ${id}`.

### `Switch Window` finds the window's page by its title

`Switch Window` needs Browser's id of the window's own page, because only `Switch Page` changes the active page. The page's title is what Browser's catalog and the main process both know:

1. For a title or a window id, the main process finds the window and returns its id and its page's title, `webContents.getTitle()`.
2. Python looks for that title among the application's pages in Browser's catalog and waits up to the library timeout until exactly one page has it. Several pages with the title fail with an error that names it.
3. It calls `Switch Page` with that page's id and checks with `isWindowPage` that the active page is the own page of that window. If not, it switches back and fails.

For a page id or `NEW`, it calls `Switch Page` directly and checks that the active page is a window's own page. In all cases it returns the previous page id, so that switching back is exact.

- **Measured:** by title, the keyword found a new window right after the click in 3 of 3 rounds, the window instead of its late `<webview>` in 3 of 3, the new window after a switch back to an older one, and a window whose application set a title of its own. In VS Code, it found a moved editor's window and an empty second window.
- **The page's title, not the window's:** the catalog lists only page titles, so a window that shows a title of its own would not be found there. The main process gives the title of the page of exactly the window that was asked for.
- **Alternatives:**
  - The order in which Browser's catalog reads the pages, observed by replacing `url()`: it relies on Browser's internals.
  - A function `pageIdOf(page)` in Browser: it needs an addition to Browser, and the title covers the cases.
  - Switching through the pages until the active one is the window: it moves the focus through the windows.

### Keywords of `Electron`, inherited by `VSCode`

The keywords are methods of `Electron`, beside `Evaluate In Main Process`, and share its check for "No application is open." `VSCode` inherits them. Its documentation changes where it names `Switch Page` for windows, for example at `Evaluate In Extension Host`.

### Tests

- **The JS harness** (`test_electron_js.py`) covers what needs no real window manager: the error with its causes when `maximize()` changes nothing, finding a window by id and by title, and the check of the active page.
- **Unit tests** (`test_library.py`) cover the search of the catalog by title with one, no and several pages, the switch back after a failed check, the forms of ids and the missing application.
- **`windows.robot`** gets the acceptance tests of the spec's scenarios with the fixture app under the display profiles, which start Openbox. The fixture app gets a second window with a `<webview>`. The error without a window manager stays with the harness, because the display profiles start one.
- **VS Code:** a test in `packages/vscode/atest/` opens a second workbench window, switches to it by its title and maximises it.

## Risks / Trade-offs

- [Titles repeat, for example in two empty VS Code windows] → The keywords fail with an error that names the windows. The size and state keywords then take the window's id; `Switch Window` takes the page id, because it goes through the page's title.
- [Titles change, VS Code puts the active file in front] → `Get Window Titles` shows the current ones, and a test gives the title of the moment. Patterns can follow.
- [The catalog lists an empty title for a page that does not answer within 350 ms] → `Switch Window` waits and reads the catalog again.
- [`NEW` lands on views and on pages that were already open] → The check catches views, and the guide recommends the title for new windows.
- [Window ids repeat across applications] → The keywords read an id in the active application, and the guide says to get the ids again after `Switch Electron Application`.
- [Window managers differ] → The keywords wait and fail with the likely causes. The display profiles start Openbox, and the guide says which displays can maximise and minimise.
- [A minimised window draws no frames, so Browser keywords on it wait until their timeout] → The guide says to call `Restore Window` first.
- [A change that the window manager ignores fails only after the library timeout] → Tests that expect it set a shorter timeout.
- [`Switch Window` focuses the target window, because `Switch Page` brings it to the front] → Wanted for a switch. `Get Window Ids`, `Get Window Titles` and the size and state keywords do not call Browser.
