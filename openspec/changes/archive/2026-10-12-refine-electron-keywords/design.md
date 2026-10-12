# Design

## Context

See proposal.md for the motivation and the spec deltas for the requirements.

- **robotlibcore:** Browser is a `DynamicCore`. It keeps its keywords in `self.keywords`, under method names such as `close_browser`, or under translated names when `language=` is given. `get_keyword_names()` returns `sorted(self.keywords)`, and `run_keyword` looks the name up in `self.keywords`.
- **Who asks for keyword names:** Robot Framework, Libdoc and RobotCode use `get_keyword_names()`, and so does Browser's `Promise To`. Browser's own code calls the methods directly, for example automatic closing calls `close_browser`, and run-on-failure looks its keyword up in `self.keywords`.
- **Spike of 2026-10-12** (a subclass of `Electron` in the scratchpad):
  - Overriding `get_keyword_names` removed the keywords from Libdoc. Calling one failed with "No keyword with name 'Close Browser' found." Automatic closing, run-on-failure and `Promise To` with visible keywords kept working, and `Promise To` refused the hidden ones.
  - A new keyword that calls `switch_browser` switched between two applications.
  - Turning links to hidden keywords in Browser's documentation into code with a regular expression did not work reliably: double backticks shift the pairs, and new broken links appeared.
- **Links into Browser's introduction:** Browser's keyword documentation links to the sections `Finding elements` (46 times), `Assertions` (24), `Browser, Context and Page` (15) and `Implicit waiting` (2). Our own `Close Electron Application` links to `Automatic page and context closing`. Types such as `DownloadInfo`, and `Importing`, resolve on their own.
- **`New Persistent Context`** attaches its context to an open application's browser entry, because Browser's `addBrowser` matches entries by `browser === null`. Hiding the keyword avoids this for our users; a fix belongs to Browser.

## Goals / Non-Goals

**Goals:**
- Users of `Electron` and `VSCode` see only keywords that make sense for applications, named after applications.
- The library documentation is our own and points to the Browser library's documentation instead of copying it.

**Non-Goals:**
- Rewriting the documentation of the Browser keywords that stay visible. Their links to hidden keywords show as plain names.
- A web browser beside an application inside `Electron`. A test that needs one imports `Browser` as well.
- Fixing `New Persistent Context` in Browser.

## Decisions

### Hiding keywords

- `Electron` overrides `get_keyword_names` and leaves out the keywords whose method is in a constant `HIDDEN_KEYWORDS`. It compares the method's `__name__`, not the registered name, so that translated names are hidden too.
- The keywords stay in `self.keywords`, so Browser's own code keeps calling them.
- `VSCode` inherits the override.
- **Alternative:** deleting the entries from `self.keywords`. Rejected: code that looks keywords up by name in `self.keywords` would break.
- A unit test checks that every name in `HIDDEN_KEYWORDS` is a method of Browser, so that a Browser release that renames one is noticed.

### Keywords for applications

- New keywords are thin methods that call Browser's methods:
  - `Switch Electron Application    application` calls `switch_browser` and returns the id of the application that was active before.
  - `Get Electron Application Ids    selection=ALL` calls `get_browser_ids`; `ACTIVE` returns the active one.
  - `Get Electron Application Catalog` returns Browser's catalog without the context level, which always has one entry: a list of applications with `id`, `active` and `pages`, each page with `id`, `title`, `url` and `active`.
- **Alternative:** a second keyword name for Browser's methods. Rejected: robotlibcore registers one name per method, and the argument names should change as well.

### `Evaluate In Main Process` requires its function

Found in the review: with `*function`, as Browser's `Evaluate JavaScript` has it, a call without any argument was valid for Robot Framework and RobotCode, and failed only at run time, with Browser's message "No Browser is open but needed for this operation." when the application was closed. The keyword now takes `function` as a required argument and `*lines` for further lines, which keeps multi-line functions with `...`. Without an open application, it fails with "No application is open."

### Argument names and return value

- `browser=CURRENT` becomes `application=CURRENT` in `Close Electron Application` and `Evaluate In Main Process`, and `instance=CURRENT` in `Close VS Code` and `Get VS Code Instance Directories`. `ALL` keeps working where it did.
- `New Electron Application` and `Open VS Code` return a tuple of the application id and the page details: `${app}    ${page} =    New Electron Application    …`.
- There are no aliases for the old names, as in the rest of the pilot phase.

### Documentation

- `_docs.py` drops `browser_sections()` and `browser_import_arguments()`. It gets a helper that links to a section of the Browser library's documentation, `https://marketsquare.github.io/robotframework-browser/Browser.html#<section>`, and the texts of the sections that both libraries share.
- The shared sections are short and named as in Browser, so that the links from Browser's keyword documentation resolve:
  - **Browser, Context and Page:** an application is a browser with one context, and its windows, `<webview>`s and `WebContentsView`s are pages. Then the comparison: a table with the Browser keyword, the keyword that `Electron` offers instead or "hidden", and the reason.
  - **Finding elements**, **Assertions**, **Implicit waiting:** one or two sentences, the link to Browser's section, and what differs in applications.
  - **Automatic page and context closing:** the application ends with the test or suite that started it.
- `Electron`'s introduction covers starting and closing applications, several applications, the main process, launch options, videos, traces and HAR files.
- `VSCode`'s introduction covers opening VS Code, instances, extensions, the workbench and the helper library, and uses the shared sections.
- **Import documentation:** each library's own short text with a link to Browser's `Importing`. Libdoc still shows Browser's import arguments with their types and defaults, without Browser's descriptions.
- **Libdoc test:** the unresolved links of `Electron` and `VSCode` may be those of Browser, plus the names of hidden keywords.
- **Notes on Browser keywords** (added in the review): Browser keywords that behave differently in applications keep Browser's documentation, followed by a note *In Electron applications*. `Electron` overrides `get_keyword_documentation` and adds the note by method name from `KEYWORD_NOTES` in `_docs.py`: `Close Page`, `Switch Page`, `Get Page Ids`, `Save Storage State`, `Handle Future Dialogs`, `Press Keys` and `Keyboard Key`. Each note says only what an acceptance test checks. Unit tests check the notes and their links in the generated Libdoc.
  - **Alternative:** overriding these keywords with own methods and documentation. Rejected: Browser's own code calls some of them, for example `close_page` during automatic closing, with Browser's arguments.

### Tests

- **Teardowns:** `Close Browser    ALL` becomes `Close Electron Application    ALL` in the Electron tests and `Close VS Code    ALL` in the VSCode tests.
- **Several applications:** the test with a web browser beside an application becomes one with two applications: switching, ids and catalog. A second test imports `Browser` beside `Electron` and opens a web page with `Browser.New Page`, which shows the migration path.
- **`main_process.robot`:** "Active Page Of Another Browser" uses a second application.
- **`limitations.robot`:** one test checks that every hidden keyword is unknown. The test of `Save Storage State` stays, because that keyword stays visible.
- **Newly checked keywords:**
  - `LocalStorage Remove Item`, `LocalStorage Clear`, `SessionStorage Remove Item` and `SessionStorage Clear` go into `context_state.robot`.
  - `Cancel Download` goes into `dialogs_and_downloads.robot`. It needs an endpoint `/slow` in the fixture's web server, which sends its body slowly. Browser's own test server buffered it, so the audit could not check it.

## Risks / Trade-offs

- [Browser adds a keyword for browsers or contexts in a later release] → It is visible until we add it to `HIDDEN_KEYWORDS`. The comparison in the documentation names the hidden keywords explicitly, so a review of a Browser upgrade can compare.
- [Browser's keyword documentation mentions hidden keywords] → They show as plain names. The section `Browser, Context and Page` explains what to use instead.
- [Two Browser-based libraries in one suite] → `Browser` and `Electron` each start a Node process, and their keywords need the library prefix. The acceptance test shows that it works.
- [Links to the Browser documentation point to its latest version, which may differ from the installed one] → Acceptable for the sections we link to, which change rarely.
- [`Close Page` on the page of a `<webview>` waits forever (found in the review on 2026-10-12): the `<webview>` element in its host page keeps the guest] → The documentation says so and shows how to remove the element; acceptance tests cover both, and `Close Page` on a `WebContentsView`.

## Migration Plan

- Archive `fix-electron-first-window` first; this change modifies the same requirement.
