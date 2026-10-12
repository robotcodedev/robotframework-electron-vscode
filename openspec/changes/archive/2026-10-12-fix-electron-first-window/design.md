# Design

## Context

See proposal.md for the motivation.

- **Browser:** `adoptContext` indexes the pages of `context.pages()` and makes the first of them the active page. The hook has no option to choose another one.
- **Playwright:** `context.pages()` lists the pages in the order in which Playwright attached to them. With a `WebContentsView` created right after the window, that order varies. `electronApplication.firstWindow()` returns the first page as well, so it can be the view.
- **Telling the pages apart** (checked on 2026-10-12, Electron 44.7, fixture app with `--views`):
  - The DevTools target type is `page` for both the window and the `WebContentsView`, and `webview` for the `<webview>`.
  - `webContents.getType()` is `window` for both the window and the `WebContentsView`.
  - `BrowserWindow.fromWebContents(wc)` returns the window for all three, but only for the window's own page is `window.webContents === wc`.
- **Reaching a page from the main process:** a CDP session on a page gives its target id through `Target.getTargetInfo`, and `webContents.fromDevToolsTargetId(id)` gives its contents in the main process.
- **Browser's page ids:** a JavaScript extension gets only the active page. Python can list the page ids of the application's context with `Get Page Ids` and switch to one with `Switch Page`.

## Goals / Non-Goals

**Goals:**
- The window's own page is the active page after `New Electron Application`, and the returned page details are its details, with views or without.

**Non-Goals:**
- Choosing among several windows that the application opens at the start. The first window is the first window page in Playwright's order, as before.
- Changes to Browser.

## Decisions

### A window's own page

- `electron.js` gets a helper that takes a page and tells whether it is a window's own page:
  1. open a CDP session on the page and read its target id;
  2. in the main process, look up its contents and compare them with the contents of the window that `BrowserWindow.fromWebContents` returns.
- A page that has closed in the meantime counts as no window page.
- **Alternative:** comparing URLs or titles. Rejected: a view can load the same page as its window, and pages that are still loading have neither.

### Waiting for the window at the start

- After `firstWindow()`, the launch checks the page.
  - If it is a window's own page, nothing changes.
  - If it is open but not a window's own page, the launch waits for further pages with `waitForEvent('window')` until a window's own page appears, within the start `timeout`.
  - If it has closed, the launch goes on as today, so that "First window closes during the start" still returns without an error.
- The video path comes from the window's own page.

### Making it the active page

- A new function `robotframeworkElectronIsWindowPage(browserId, page)` tells whether the active page is a window's own page of that application.
- After `adoptContext`, `New Electron Application` asks it. If the active page is a view, the keyword goes through the page ids of the application's context and switches to each with `Switch Page` until the function says yes. It returns that page's id in the page details.
- This happens only when the active page is not the window, so most applications pay one call.
- **Alternative:** an option of the `adoptContext` hook that names the active page. Rejected for now: it needs a change to Browser and a release, and changes to Browser are agreed with its maintainer first. It would replace the search if Browser gets it later.
- **Alternative:** mapping the index in `context.pages()` to the order of Browser's page ids. Rejected: it relies on the internal order of Browser's page stack.
- **Side effect:** `Switch Page` brings the pages it tries to the front, once, at the start.

### Tests

- **Acceptance test** in `start_application.robot`, "Browser Keywords Act On The First Window With Views":
  - It starts the fixture app with `--views` three times, because the order varies. Each time, the active page's title is the window's and the returned page id is the active page's.
  - It is written and run before the fix, and must fail there. On 2026-10-12, it failed with "Title 'View' (str) should be 'Views' (str)": the view was the active page.
- **`pages.robot`:** the test with `>>>` no longer switches to the window by title.
- **Unit tests:**
  - `test_electron_js.py`: the launch waits for a window page after a view, returns the window page's video path, and goes on when the first page has closed.
  - `test_library.py`: the keyword switches to the window page when the active page is a view, and does not switch otherwise.

## Risks / Trade-offs

- [A slower start when the view comes first] → One more check per page tried, and a wait only until the window's page appears.
- [An application that closes its first window and opens another one] → The launch waits only while the first page is open, as described above; a later window is found by the search in Python.
