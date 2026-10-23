# Tasks

## 1. Finding windows

- [ ] 1.1 In `packages/electron/src/Electron/electron.js`, turn `isWindowPage` into a function that returns the id of the window whose own page a page is, or `null`, and keep `firstWindowPage` on it; verify with the existing tests in `packages/electron/tests/test_electron_js.py` and with `uv run robotcode -r . -p xvfb robot packages/electron/atest/start_application.robot`.
- [ ] 1.2 In `electron.js`, add the window lookup: an id as `window=<n>` or as a bare number through `BrowserWindow.fromId()`, `title=<title>` through `getTitle()` over `getAllWindows()`, polled until exactly one window shows the title or `defaultTimeout` is over, and without a window the window of the active page through `browserWindow(page)`; the errors name the id, or the title and how many windows show it. Verify with JS harness tests for each form, an unknown id, a title that appears late and a title of two windows.
- [ ] 1.3 Add `Get Window Ids` (`ALL` or `ACTIVE`, sorted by id, as `window=<n>`) and `Get Window Titles` to `packages/electron/src/Electron/__init__.py`, with the check for "No application is open." shared with `Evaluate In Main Process` and keyword documentation with examples; verify with unit tests in `packages/electron/tests/test_library.py` for the id format, `ACTIVE` and the missing application.
- [ ] 1.4 Add acceptance tests to `packages/electron/atest/windows.robot` for the scenarios of "Window ids" and "Window titles"; verify with `uv run robotcode -r . -p xvfb robot packages/electron/atest/windows.robot`.
- [ ] 1.5 Describe window ids and titles in the library introduction's section "Windows and pages" in `Electron/__init__.py`, and in the section "Browser, Context and Page" and the note of `Get Page Ids` in `packages/electron/src/Electron/_docs.py`; verify that `uv run python -m robot.libdoc Electron` with an output file in the scratchpad builds and links `Get Window Ids` and `Get Window Titles`.

## 2. Size and state

- [ ] 2.1 In `electron.js`, add the functions that set and read a window's content size and state: they poll every 50 ms until the window has the requested state or size or `defaultTimeout` is over, restore with `restore()` and then `unmaximize()`, make the window normal before `setContentSize()`, allow 2 pixels at a fractional display scale, and throw an error with the requested and the actual state or size and the likely causes; verify with JS harness tests for a window whose `maximize()` changes nothing, a window that was maximised before it was minimised, and a fractional display scale.
- [ ] 2.2 Add `Set Window Size`, `Get Window Size`, `Maximize Window`, `Minimize Window`, `Restore Window` and `Get Window State` to `Electron`, with the window as last argument, Browser's `SizeFields`, assertion operators and `with_assertion_polling` for the getters, and keyword documentation; verify with unit tests for the forms of the window, the arguments that reach `electron.js` and a failing assertion.
- [ ] 2.3 Add acceptance tests to `windows.robot` for the scenarios of "Giving a window", "Window of the size and state keywords", the size and state requirements and "Window keywords need an application"; verify under `-p xvfb`, which starts Openbox.
- [ ] 2.4 Add a note to `Get Viewport Size` in `_docs.py` that it returns `None` for an application's window and that `Get Window Size` returns the size, with a test in `packages/electron/atest/browser_keywords/electron_behaviour.robot`; verify under `-p xvfb`.
- [ ] 2.5 Replace the main-process workaround for sizing and maximising in the documentation of `Evaluate In Main Process`, in the sections on the main process and on the behaviour of Electron in `docs/src/content/docs/electron/getting-started.md` and `browser-keywords.md`, and describe in `docs/src/content/docs/running/ci-and-display.mdx` which displays can maximise and minimise and that a minimised window draws nothing until `Restore Window`; verify with `npm run build` in `docs/`.

## 3. Switching windows

- [ ] 3.1 Add to `Electron` the search of Browser's catalog for the application's page with a given title: it waits up to the library timeout until exactly one page has the title, also while the catalog lists an empty title for a busy page, and fails with an error that names the title when several pages have it; verify with unit tests for one, no, several and late pages.
- [ ] 3.2 Add `Switch Window` to `Electron`. For a title or a window id, it gets the window and its page's title from the main process and the page id from the catalog. It calls `Switch Page` and checks that the active page is that window's own page. For a page id or `NEW`, it calls `Switch Page` and checks that the active page is a window's own page. When a check fails, it switches back and fails. It returns the previous page id and has keyword documentation. Verify with unit tests for each form and for the switch back.
- [ ] 3.3 Give the fixture app in `packages/electron/atest/fixtures/app/` a second window that shows a `<webview>` and a title of its own; verify with a test that `Get Window Titles` lists the window and that `Get Page Ids` has the page of its `<webview>`.
- [ ] 3.4 Add acceptance tests to `windows.robot` for the scenarios of "Switch to a window", "Switch to a page of a window" and "Switch to a new window"; verify under `-p xvfb`.
- [ ] 3.5 Document switching in `docs/src/content/docs/electron/browser-keywords.md`: the table row and the section on pages and windows recommend `Switch Window` with the title, explain why `NEW` can select a view or a page that was open before, and select views and `<webview>`s by their page id from `Get Electron Application Catalog` instead of switching through all pages, also in the copy of that keyword in `packages/electron/atest/browser_keywords/pages.robot`. Update as well the section on windows in `getting-started.md`, the documentation of `Start Electron Application` and the note of `Switch Page` in `_docs.py`. Verify with `npm run build` in `docs/` and `pages.robot` under `-p xvfb`.

## 4. VS Code

- [ ] 4.1 Add `packages/vscode/atest/windows.robot`, which opens a second workbench window, switches to it with `Switch Window` and its title, and maximises it; verify with `uv run robotcode -r . -p xvfb robot packages/vscode/atest/windows.robot`.
- [ ] 4.2 Point the documentation of `Evaluate In Extension Host` in `packages/vscode/src/VSCode/__init__.py` and the VS Code guides `browser-keywords.md`, `videos-and-traces.mdx` and `extension-host.md` in `docs/src/content/docs/vscode/` to `Switch Window` and the size and state keywords; verify with `npm run build` in `docs/`.
- [ ] 4.3 Switch windows in `examples/vscode-extension/tests/windows.robot` with `Switch Window` and count them with `Get Window Ids`, and check the guide that points to the file; verify with `uv run robotcode -r examples/vscode-extension -p xvfb robot` after `npm ci` and `npm run download-vscode` in `examples/vscode-extension/`.

## 5. Integration

- [ ] 5.1 Run `uv run pytest`, `uv run robotcode -r . -p xvfb robot` and `uv run robotcode -r . -p xvfb -p electron-previous robot packages/electron/atest/windows.robot`, and verify that all tests pass.
- [ ] 5.2 Run `uv run pre-commit run --all-files` and verify that ruff, mypy and RobotCode's analysis pass.

## Workflow follow-up

- Delete `playground/window-keywords.md`, which this change replaces.
- Archive the change with `/opsx:archive` once it is implemented and reviewed.
