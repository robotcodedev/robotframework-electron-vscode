# Design

## Context

See proposal.md for the motivation and the spec deltas for the requirements.

- **The audit of 2026-10-11:** every keyword of the `Electron` library was tried on a probe app with Electron 44.7 and Playwright 1.63, under Xvfb, and compared with headless Chromium where the cause was unclear. The results are in a local note that is not in git.
  - Most keywords work as in Chromium.
  - `New Page`, `New Context`, `Set Storage State`, `Crawl Site`, `Tap` and `Save Page As Pdf` fail on the application, each with a protocol or Playwright error.
  - Some behaviours of Electron surprise:
    - `prompt()` is not implemented;
    - shortcuts do not reach menu accelerators or `before-input-event`;
    - `Switch Page    NEW` does not find `<webview>`s and `WebContentsView`s;
    - an application that quits by itself stays in Browser's catalog.
  - Two crashes end Browser's Node process: a `beforeunload` handler (Playwright), and `Handle Future Dialogs` with `Wait For Alert` on the same page (Browser).
- **The current guide:** `guides/browser-features.md`, "Browser features in VS Code", has a table of features with VS Code results and snippets that assume an open VS Code.
- **The fixture app:** one window with `index.html`. A second window opens from a button. `ElectronFixture.py` serves a small web server for the download test. With `add-electron-launch-options`, the app gets `--page` to load another page.
- **User data:** the fixture app keeps its user data in `~/.config/robotframework-electron-fixture`, so cookies and local storage last from one run to the next.

## Goals / Non-Goals

**Goals:**
- One guide that answers "does this Browser keyword work on my application, and if not, what instead".
- Tests that notice when an upgrade changes one of its answers.

**Non-Goals:**
- A test per keyword. Browser tests its keywords itself; ours check that each group works on an application.
- Tests for the two crashes. They end Browser's Node process and with it the whole run.
- Fixing the crashes or the errors. They belong to Playwright and Browser.
- Packaged applications and the way in over CDP.

## Decisions

### One guide instead of two

- `guides/browser-keywords.md`, titled "Browser keywords in applications", replaces `guides/browser-features.md`.
- **Alternative:** a second guide for Electron next to the VS Code guide. Rejected: both would list the same groups and limitations.
- The old URL goes away without a redirect. In the pilot phase, there are no outside links to keep.

### Structure of the guide

1. **How an application looks to Browser:**
   - one browser with one context, whose windows are pages;
   - `New Browser`, `New Context` and `New Page` create a web browser beside the application;
   - other settings mean starting the application again.
2. **Overview:** a table per group. It says whether the group works and names each keyword that fails or behaves differently.
   - The groups are locators, reading content, input, waiting, context state, dialogs, downloads, pages and windows, screenshots and recordings, and configuration.
   - The table does not list all 152 keywords. Such a list would be long, would be outdated with every Browser release, and would repeat Browser's own documentation.
3. **Keywords that fail:** a table with the keyword, its error and the cause.
4. **Behaviour of Electron:** for example the color scheme, viewport, locale and time zone, user data, shortcuts and menus, native dialogs, and `<webview>`s. Each entry names what to use instead where there is something, such as `color_scheme`, `locale` or `Evaluate In Main Process`.
5. **Known crashes:** both crashes, with workarounds only where they were checked.
6. **In VS Code:** the VS Code rows of the old table and its snippets.

The guide names the versions its results come from, as the old one does.

### Snippets

- The guide has its snippets inline, as the old one.
- Each snippet does what a test in the suites does, so that it is checked.
- **Alternative:** including the suites with `<Code>`. Rejected: a suite holds the setup and assertions for many cases, and a reader needs three lines.

### Acceptance tests

- **Folder:** `packages/electron/atest/browser_keywords/`, one suite per group:
  - `locators.robot`;
  - `content_and_input.robot`;
  - `waiting.robot`;
  - `context_state.robot`;
  - `dialogs_and_downloads.robot`;
  - `pages.robot`;
  - `electron_behaviour.robot`;
  - `limitations.robot`.
- **Tests:** one test per part of a group, with several keywords each, for example "Form Input" or "Cookies".
- **Starting the app:** a suite starts the fixture app once, in its suite setup. A suite whose tests leave state behind that the next test would see, such as dialog handlers, starts it per test.
- **Limitations:** `limitations.robot` runs each failing keyword with `Run Keyword And Expect Error` and the error that the guide quotes. Each test's documentation says what to do when it fails after an upgrade: update the guide, and turn the test into one that uses the keyword.

### Fixture app

- **Pages**, each loaded with `--page`:
  - `keywords.html`: form elements, a table, a shadow root, a same-origin iframe, buttons for `alert`, `confirm` and `prompt`, a download link, and elements with roles and test ids;
  - small pages for the `<webview>`, the `WebContentsView` and the iframe.
- **`--views`:** the main window shows a `<webview>` and gets a `WebContentsView`.
- **Menu:** an application menu with an item that has an accelerator and writes into the page when it is clicked. The behaviour test shows that `Press Keys` with the accelerator does not trigger it, and that `Evaluate In Main Process` can click it.

### Fresh user data

- `Start Fixture App` passes `--user-data-dir` with a new, empty folder under `${OUTPUT_DIR}/electron-user-data` for every start. The one test that starts the app with a relative executable path does the same.
- A fresh folder per start, and not per suite, because some tests start two applications at once, and two instances must not share a profile.

## Risks / Trade-offs

- [A test pinned to an error fails after an upgrade that improves Browser or Playwright] → That is the purpose. The test's documentation says what to change.
- [The guide states results that no test checks, such as WebAuthn or coverage] → The suites check every group. Results of single keywords come from the audit and are named with their versions.
- [The suites make the Electron run longer] → One start per suite and tests per group, not per keyword.
- [The change depends on two open changes] → It is implemented after `add-electron-launch-options` and `add-electron-main-evaluate`. Started earlier, the guide would show workarounds that those changes replace.
