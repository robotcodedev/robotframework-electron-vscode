# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Drop-in replacement for Browser`
- TO: `### Requirement: Browser keywords for applications`

## MODIFIED Requirements

### Requirement: Browser keywords for applications
The `Electron` library SHALL provide the Browser library's keywords that apply to an application, together with Browser's import arguments and their behaviour, in addition to its own keywords. It SHALL hide Browser's keywords that create, switch, list or close browsers and contexts, and those that cannot work on an application, and its documentation SHALL name them. It SHALL add no import arguments of its own.

#### Scenario: Browser keywords without Browser
- **WHEN** a suite imports `Electron` and does not import `Browser`
- **THEN** Browser keywords such as `Click` and `Get Text` can be called without a library prefix

#### Scenario: Browser import arguments
- **WHEN** a suite imports `Electron    timeout=5s    auto_closing_level=SUITE`
- **THEN** both settings take effect exactly as they do for `Browser    timeout=5s    auto_closing_level=SUITE`

#### Scenario: Hidden keyword
- **WHEN** a suite that imports only `Electron` calls `New Context`
- **THEN** it fails because no such keyword exists, and the library's documentation does not list it

### Requirement: Library documentation
The library documentation SHALL be the `Electron` library's own, with import documentation that links to the Browser library's import arguments. The sections that Browser keywords link to SHALL exist with short texts that point to the Browser library's documentation. Browser keywords that behave differently in applications SHALL have a note on it. The documentation SHALL report the version of the `Electron` library, not that of Browser.

#### Scenario: Generated documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** it reports the version of `robotframework-electron`, and links in the Browser keyword documentation, such as those to `Assertions`, resolve to sections of the same document

#### Scenario: Own introduction
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** the introduction consists of the `Electron` library's own text, and its section `Assertions` links to the Browser library's documentation instead of repeating it

#### Scenario: Own import documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** the import documentation is the `Electron` library's own text with a link to the Browser library's import arguments, and the import arguments are Browser's, with their types and defaults

#### Scenario: Comparison with the Browser library
- **WHEN** someone looks up `New Context` in the documentation of `Electron`
- **THEN** the section `Browser, Context and Page` says that the library hides it, why, and what to use instead

#### Scenario: Note on a Browser keyword
- **WHEN** someone looks up `Close Page` in the documentation of `Electron`
- **THEN** it says, after Browser's text, that `Close Page` waits forever on the page of a `<webview>` and how to remove the `<webview>` instead

### Requirement: Windows are Browser pages
A started application SHALL be a browser in Browser's state with one context. Each of its windows SHALL be a page of that context, and its first window SHALL be the active page when `New Electron Application` returns, also when the application shows `WebContentsView`s or `<webview>`s, which are pages of the context as well.

#### Scenario: Browser keywords act on the first window
- **WHEN** an application has been started
- **THEN** `Get Title` returns the title of its first window and `Click` acts on that window

#### Scenario: Return value
- **WHEN** an application has been started
- **THEN** the keyword returns the application id and the details of the first window's page

#### Scenario: Views at the start
- **WHEN** an application shows a `WebContentsView` and a `<webview>` in its first window when it starts
- **THEN** the window's own page is the active page, and the returned page details are those of that page

### Requirement: Close an application
`Close Electron Application` SHALL end the active application, all applications, or the application whose id is given, and SHALL remove it from Browser's state. It SHALL return only after the application process has exited. It SHALL also succeed if the application has already exited.

#### Scenario: Close the active application
- **WHEN** `Close Electron Application` is called while another application was active before the closed one
- **THEN** the application process has exited when the keyword returns, and the application that was active before becomes active again

#### Scenario: Close by browser id
- **WHEN** the keyword is called with the id of an application that is not the active one
- **THEN** that application ends and the active application stays active

#### Scenario: Application already exited
- **WHEN** the application has quit on its own and `Close Electron Application` is called
- **THEN** the keyword passes

### Requirement: Browser's closing ends the application
An application SHALL end whenever Browser closes it: through `Close Electron Application`, through automatic closing at the end of the test or suite that started it, and at the end of the run.

#### Scenario: Started in a test
- **WHEN** a test starts an application and the library uses the default automatic closing level
- **THEN** the application process has ended after the test

#### Scenario: Started in a suite setup
- **WHEN** a suite setup starts an application
- **THEN** the application stays open for all tests of the suite and ends after the suite

#### Scenario: End of the run
- **WHEN** the run ends while an application is still open
- **THEN** the application process ends

### Requirement: Evaluate in the main process
`Evaluate In Main Process` SHALL run a JavaScript function in the main process of an application started by `New Electron Application`, the active one or the one with a given application id. The function SHALL be a required argument; further arguments continue it. It SHALL get the `electron` module and the keyword's `arg`, and the keyword SHALL return the function's result. Without an open application, or for an id that is not such an application, it SHALL fail with a message that says so.

#### Scenario: Value from the main process
- **WHEN** a test evaluates `({ app }) => app.getName()` in the main process of the fixture app
- **THEN** the keyword returns the name from the fixture app's `package.json`

#### Scenario: Native dialog replaced
- **WHEN** a test replaces `dialog.showOpenDialog` in the main process with a function that returns a fixed path, and then clicks the fixture app's button that opens a file dialog
- **THEN** no dialog opens, and the page shows the fixed path

#### Scenario: Not an Electron application
- **WHEN** `Evaluate In Main Process` is called with an application id that `New Electron Application` did not return
- **THEN** it fails with a message that names the id

#### Scenario: No application open
- **WHEN** `Evaluate In Main Process` is called while no application is open
- **THEN** it fails with "No application is open."

#### Scenario: Call without a function
- **WHEN** a test calls `Evaluate In Main Process` without a function
- **THEN** Robot Framework, and RobotCode's analysis, report the missing argument

### Requirement: Window of the active page
The function that `Evaluate In Main Process` runs SHALL get, after `arg`, the `BrowserWindow` that shows the active page. If the active page is not one of that application's, it SHALL get `null` instead.

#### Scenario: Window sized from the main process
- **WHEN** a test sets the bounds of the window it gets in the main process to 1024×700
- **THEN** the active page's window is 1024×700

#### Scenario: Window of the active page
- **WHEN** the fixture app has opened its second window, a test switches to that window's page with `Switch Page`, and evaluates `(electron, arg, window) => window.getTitle()`
- **THEN** the keyword returns the second window's title

#### Scenario: Active page of another browser
- **WHEN** another application is active, and a test evaluates `(electron, arg, window) => window === null` in the fixture app's main process with the fixture app's id
- **THEN** the keyword returns `True`

### Requirement: Browser keywords on application windows
Browser's keywords for locating elements, reading and input, waiting, context state, dialogs and downloads SHALL work on the windows of an application as they do on the pages of a web browser. Pages without a window of their own, such as `<webview>` guests and `WebContentsView`s, SHALL be selectable by their page id.

#### Scenario: Locators in a window
- **WHEN** a test locates elements in a window of the fixture app with CSS, XPath, text, id, role and test id selectors, through a shadow root, and in an iframe with `>>>`
- **THEN** each selector finds its element

#### Scenario: Context state
- **WHEN** a test adds a cookie and entries in local and session storage in a window of the fixture app, and removes and clears them again
- **THEN** `Get Cookie`, `LocalStorage Get Item` and `SessionStorage Get Item` return what is there at each step

#### Scenario: Dialogs
- **WHEN** a test accepts an `alert` and a `confirm` of the fixture app with `Handle Future Dialogs`
- **THEN** the page sees the confirmation

#### Scenario: Download after a click
- **WHEN** a test clicks a download link in the fixture app with `Promise To Wait For Download`
- **THEN** the downloaded file is saved where the test asked

#### Scenario: Pages without a window
- **WHEN** the fixture app shows a `<webview>` and a `WebContentsView`
- **THEN** both are pages in `Get Electron Application Catalog`, and after `Switch Page` with their page ids, Browser keywords act on them

#### Scenario: Cancelled download
- **WHEN** a test starts a download that a web server sends slowly, and cancels it with `Cancel Download`
- **THEN** `Get Download State` reports it as canceled

### Requirement: Guide on Browser keywords
The documentation site SHALL have a guide that says, for each group of Browser keywords, what works on an application, which Browser keywords the libraries hide and what to use instead, which keywords fail and why, and which behaviours of Electron tests need to know. For each visible keyword that the guide lists as failing, an acceptance test SHALL expect its error.

#### Scenario: A keyword that fails
- **WHEN** someone looks up `Save Page As PDF` in the guide
- **THEN** the guide says that the libraries hide it, because it fails on applications, and why

#### Scenario: A behaviour of Electron
- **WHEN** someone looks up why `Press Keys` does not trigger a menu item's accelerator
- **THEN** the guide explains it and shows how to click the menu item in the main process instead

#### Scenario: A limitation lifted by an upgrade
- **WHEN** a Browser or Playwright upgrade makes a keyword work that the guide lists as failing
- **THEN** the acceptance test for that keyword fails

## ADDED Requirements

### Requirement: Several applications
Several applications SHALL be open at the same time, each a browser of its own in Browser's state. `Switch Electron Application` SHALL make another application the active one, `Get Electron Application Ids` SHALL return the ids of the open applications, and `Get Electron Application Catalog` SHALL return the open applications with their pages.

#### Scenario: Switch between applications
- **WHEN** a test starts two applications and calls `Switch Electron Application` with the id of the first
- **THEN** the first application's window is the active page

#### Scenario: Ids of the open applications
- **WHEN** two applications are open
- **THEN** `Get Electron Application Ids` returns both ids, and with `ACTIVE` only the id of the active one

#### Scenario: Catalog of the applications
- **WHEN** an application with a second window is open
- **THEN** `Get Electron Application Catalog` returns the application with both pages and their titles

## REMOVED Requirements

### Requirement: Applications and browsers side by side
**Reason**: A web browser beside an application needs Browser's keywords for browsers, contexts and pages, which the library hides now. Switching between applications is covered by "Several applications".
**Migration**: A test that needs a web browser as well imports `Browser` beside `Electron` and calls its keywords with the library prefix, for example `Browser.New Page`.
