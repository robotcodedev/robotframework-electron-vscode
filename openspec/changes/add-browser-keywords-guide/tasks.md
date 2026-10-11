# Tasks

Before starting: `add-electron-launch-options` and `add-electron-main-evaluate` are implemented.

## 1. Fixture

- [ ] 1.1 Give every start of the fixture app a new, empty `--user-data-dir` under `${OUTPUT_DIR}/electron-user-data`, in `Start Fixture App` and in the test with a relative executable path. Verify that the Electron acceptance tests pass with `-p xvfb` and that `~/.config/robotframework-electron-fixture` is not touched by a run.
- [ ] 1.2 Add `keywords.html` and the pages for the iframe, the `<webview>` and the `WebContentsView`, the argument `--views` and the application menu to the fixture app. Verify that the existing Electron acceptance tests still pass.

## 2. Guide

- [ ] 2.1 Replace `guides/browser-features.md` with `guides/browser-keywords.md`: the introduction on how an application looks to Browser, an empty overview for the groups, and the section "In VS Code" with the old guide's VS Code rows and snippets. Update the links in the getting-started pages. Verify that `npm run build` in `docs/` succeeds with no broken links.

## 3. Keyword groups

Each task adds a suite in `packages/electron/atest/browser_keywords/` and the matching part of the guide. Verify each with the Electron acceptance tests under `-p xvfb` and `npm run build` in `docs/`.

- [ ] 3.1 Locators: `locators.robot` and the guide's row and notes on locators, including `aria-ref`, `_react` and `_vue`, and custom selector engines.
- [ ] 3.2 Content and input: `content_and_input.robot` and the rows for reading content, input, screenshots and recordings.
- [ ] 3.3 Waiting: `waiting.robot` and its row.
- [ ] 3.4 Context state: `context_state.robot` (cookies, storage, emulation, clock) and its row.
- [ ] 3.5 Dialogs and downloads: `dialogs_and_downloads.robot` and their rows, and the section on known crashes.
- [ ] 3.6 Pages and windows: `pages.robot` (second window, `<webview>` and `WebContentsView` by page id, a window closed by the app, an app that quits by itself) and its row.
- [ ] 3.7 Behaviour of Electron: `electron_behaviour.robot` (menu accelerator and `Evaluate In Main Process`, `prompt()`, viewport, color scheme, locale and time zone) and the guide's section on it.
- [ ] 3.8 Limitations: `limitations.robot` with one test per failing keyword, and the guide's table of keywords that fail.

## 4. Check

- [ ] 4.1 Run all acceptance tests of both packages with `-p xvfb`, `uv run pre-commit run --all-files` and `npm run build` in `docs/`. Read the guide on the local site and check that every snippet matches a test.
