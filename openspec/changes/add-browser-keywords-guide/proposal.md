# Proposal

## Why

The `Electron` and `VSCode` libraries contain every Browser keyword, but nothing tells users which of them work on an application, which fail, and where Electron behaves differently from a web browser. The keyword audit of 2026-10-11 found the answers: most keywords work as in Chromium, a few fail with protocol errors, and some behaviours surprise, for example shortcuts that never reach a menu accelerator, `<webview>`s that `Switch Page    NEW` does not find, or a `beforeunload` handler that crashes Browser's Node process. Today these findings exist only in a local note. The only guide, "Browser features in VS Code", covers VS Code, and no acceptance test pins the results, so a Browser or Playwright upgrade can change them unnoticed.

## What Changes

- **Guide:** "Browser keywords in applications" replaces "Browser features in VS Code". For each group of Browser keywords, it says what works on an application, which keywords fail and why, and which behaviours of Electron tests need to know. It ends with a section on VS Code that keeps the VS Code rows and snippets of the old guide.
- **Acceptance tests:** a suite per keyword group runs on the Electron fixture app: locators, content and input, waiting, context state, dialogs and downloads, pages and windows, and the keywords that fail. They test groups, not every keyword; Browser tests its keywords itself.
- **Limitations are pinned:** each keyword that the guide lists as failing has a test that expects its error. When an upgrade lifts a limitation, the test fails, and the guide gets updated.
- **Fixture app:** pages for the keyword groups, a `<webview>`, a `WebContentsView` and a menu item with an accelerator.
- **Fresh user data:** the Electron acceptance tests start the fixture app with its own user-data directory in the output directory, instead of `~/.config/robotframework-electron-fixture`, so that cookies and storage of earlier runs do not leak into the tests.
- **Order:** this change comes after `add-electron-launch-options` and `add-electron-main-evaluate`. The guide points to their arguments and keyword for the color scheme, native dialogs and menus.
- **Not part of this change:** packaged applications that cannot be launched by Playwright, and the way in over CDP. They get their own change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: Browser keywords on the windows of an application, and the guide on them.
- `vscode-examples`: the guide on Browser features becomes the VS Code section of the new guide.

## Impact

- `docs/src/content/docs/guides/`: `browser-keywords.md` replaces `browser-features.md`; links in the getting-started pages.
- `packages/electron/atest/`: a folder `browser_keywords/` with the new suites, and the fixture resource and app.
- No library code changes.
