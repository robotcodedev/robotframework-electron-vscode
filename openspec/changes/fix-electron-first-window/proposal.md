# Proposal

## Why

`New Electron Application` SHALL make the application's first window the active page (requirement "Windows are Browser pages"). An application that shows a `WebContentsView` or a `<webview>` when it starts breaks this: those are pages of the same context, Browser makes the page that Playwright saw first the active one, and that is often the view. With the fixture app and `--views`, the view was active in three of four starts on 2026-10-12. Browser keywords then act on the view instead of the window, and the returned page details belong to the view.

The existing test "Browser Keywords Act On The First Window" cannot notice it, because the fixture app shows no views there.

## What Changes

- **Test first:** an acceptance test starts the fixture app with `--views` and expects the window to be the active page. It fails before the fix.
- **Fix:** `New Electron Application` waits until the first window's own page exists, makes it the active page, and returns its page details and its video path. A page is a window's own page when its contents are the contents of a `BrowserWindow`, not a view or `<webview>` that the window shows.
- **No change to Browser:** the library finds the window's page itself and switches to it with Browser's own page switching.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: "Windows are Browser pages" gets a scenario for an application with views at the start.

## Impact

- `packages/electron/src/Electron/__init__.py` and `electron.js`, with unit tests.
- `packages/electron/atest/start_application.robot`.
- `packages/electron/atest/browser_keywords/pages.robot` no longer needs to switch to the window by title.
