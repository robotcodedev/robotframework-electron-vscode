# Proposal

## Why

`Electron` and `VSCode` contain every Browser keyword. Many of them make no sense for an application, and some fail on it:

- **Browsers and contexts:** an application is one browser with exactly one context. Keywords that create, switch or close browsers and contexts (`New Browser`, `New Context`, `Switch Context`, `Close Context` …) either fail on it or duplicate what our own keywords do. `New Persistent Context` even attaches its context to the browser entry of an open application, because Browser matches both by `browser: null` (checked on 2026-10-12).
- **Keywords that fail on an application:** `New Page`, `Crawl Site`, `Set Storage State`, `Tap`, `Save Page As Pdf`.
- **Names:** with several applications open at once, the user switches between applications, not browsers. `Switch Browser` and `Get Browser Ids` say the wrong thing.
- **Documentation:** the libraries copy Browser's introduction and import documentation. That text is about browsers, contexts and web pages, and it links to keywords that applications do not need.

## What Changes

- **Hidden keywords:** `Electron`, and with it `VSCode`, no longer offer 21 Browser keywords:
  - browsers: `New Browser`, `Open Browser`, `Close Browser`, `Switch Browser`, `Get Browser Ids`, `Get Browser Catalog`, `Launch Browser Server`, `Close Browser Server`, `Connect To Browser`;
  - contexts: `New Context`, `New Persistent Context`, `Close Context`, `Switch Context`, `Get Context Ids`;
  - pages and devices: `New Page`, `Get Device`, `Get Devices`, `Crawl Site`;
  - failing on applications: `Set Storage State`, `Tap`, `Save Page As Pdf`.
- **Keywords for applications:** `Switch Electron Application`, `Get Electron Application Ids` and `Get Electron Application Catalog` replace the corresponding Browser keywords. `Close Electron Application` replaces `Close Browser` and `Close Context`.
- **Argument names:** `browser=` becomes `application=` in `Close Electron Application` and `Evaluate In Main Process`, and `instance=` in `Close VS Code` and `Get VS Code Instance Directories`.
- **Return value:** `New Electron Application` and `Open VS Code` return the application id and the details of the first window's page, without the context id.
- **No web browser beside an application:** a test that needs a web browser as well imports `Browser` on its own.
- **Own documentation:** both libraries get their own introduction and import documentation instead of Browser's.
  - The sections that Browser's keyword documentation links to (`Browser, Context and Page`, `Finding elements`, `Assertions`, `Implicit waiting`, `Automatic page and context closing`) exist with short texts. They point to the Browser library's documentation for details, and add what is specific to Electron.
  - `Browser, Context and Page` holds a comparison with the Browser library: which keyword an application uses instead, and which keywords are hidden and why.
- **Guide:** "Browser keywords in applications" gets the same comparison. `Cancel Download` and the storage keywords that were not checked yet are now tested.
- In the pilot phase, these changes need no compatibility aliases.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `electron-applications`: the set of keywords, the new keywords for applications, argument names, the return value, the documentation, and the guide's comparison.
- `vscode-launch`: the keywords of `VSCode`, `Open VS Code`'s return value, argument names and the documentation.

## Impact

- `packages/electron/src/Electron/__init__.py` and `_docs.py`, `packages/vscode/src/VSCode/__init__.py`, with their unit tests.
- Almost all acceptance tests of both packages: `Close Browser    ALL` in teardowns becomes `Close Electron Application    ALL`. The tests with a web browser beside an application change.
- `docs/`: the guide on Browser keywords and the getting-started pages, which mention `Close Browser`, `Close Context` and `New Context`.
- Depends on `fix-electron-first-window`, which changes "Windows are Browser pages" too and is archived first.
