# electron-applications Specification

## Purpose

Lets Robot Framework tests start Electron applications, drive their windows with the Browser library's keywords, and close the applications again, so that an Electron app can be tested like a web page.

## Requirements

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

### Requirement: Import starts nothing
Importing the `Electron` library, including generating its documentation or analysing it in an editor, SHALL NOT start the Playwright process or an application.

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** no Node.js process and no application process is started

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

### Requirement: Start an application
`New Electron Application` SHALL start the Electron application at a given executable path, or a command on `PATH`, and SHALL return once the application's first window has opened. How long it waits for that window SHALL be configurable per call. Command-line arguments, a working directory and environment variables SHALL be passed to the application as given. A relative executable path and a relative working directory SHALL be relative to the test run's working directory, and without a working directory the application SHALL run in the test run's working directory. If no environment variables are given, the application SHALL inherit the environment of the test run without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Application opens a window
- **WHEN** `New Electron Application` is called with the path of an Electron application
- **THEN** the keyword returns after the application's first window has opened

#### Scenario: Arguments and environment
- **WHEN** the keyword is called with command-line arguments, a working directory and environment variables
- **THEN** the application receives these arguments, runs in that directory and sees exactly these environment variables

#### Scenario: Test run started from inside VS Code
- **WHEN** the test run has `ELECTRON_RUN_AS_NODE=1` in its environment, as runs started from VS Code do, and no environment variables are given
- **THEN** the application starts normally and does not see `ELECTRON_RUN_AS_NODE`

#### Scenario: Default working directory
- **WHEN** the keyword is called without a working directory
- **THEN** the application runs in the test run's working directory

#### Scenario: Relative executable path
- **WHEN** the keyword is called with an executable path relative to the test run's working directory
- **THEN** the application starts

#### Scenario: First window closes during the start
- **WHEN** the application's first window closes while the keyword takes the application over
- **THEN** the keyword returns without an error, and windows that the application opens later can be selected with `Switch Page`

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

### Requirement: Further windows
Windows that the application opens later SHALL become pages of its context without becoming the active page. Closing such a page SHALL close the window.

#### Scenario: Second window
- **WHEN** the application opens a second window
- **THEN** `Switch Page    NEW` makes that window the active page

#### Scenario: Closing a window
- **WHEN** `Close Page` is called while a window of the application is the active page
- **THEN** that window closes

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

### Requirement: Failed start
If the application cannot be started, opens no window within the time allowed, or cannot be taken over by the Browser library, `New Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state.

#### Scenario: Wrong executable path
- **WHEN** the executable path does not exist
- **THEN** the keyword fails with an error that names the path

#### Scenario: No window
- **WHEN** the application opens no window within the time allowed
- **THEN** the keyword fails, and afterwards no process of the application is running

#### Scenario: Browser cannot take the application over
- **WHEN** the Browser library cannot take over the started application, for example because it has no `adoptContext` hook
- **THEN** the keyword fails with an error that names the cause, and afterwards no process of the application is running

### Requirement: Video recording
`New Electron Application` SHALL record a video of the application's windows when it is given `record_video`. It SHALL store the video in Browser's video folder of the output directory unless `record_video` names a folder, return the video's path in the page details of its return value, and embed the video in the log, as Browser does for `New Context`.

#### Scenario: Video of an application
- **WHEN** a test starts an application with `record_video`, acts in its window and closes it
- **THEN** a video of the window exists at the path in the returned page details, and the log embeds it

#### Scenario: Action overlay
- **WHEN** `record_video` contains `showActions`
- **THEN** the video shows the performed actions

#### Scenario: No recording by default
- **WHEN** a test starts an application without `record_video`
- **THEN** no video is recorded, and the video path in the page details is empty

### Requirement: Tracing
`New Electron Application` SHALL record a Playwright trace of the application when it is given `tracing`, with the values and paths of `tracing` of Browser's `New Context`, and also when the variable or environment variable `ROBOT_FRAMEWORK_BROWSER_TRACING` is `True`. The trace SHALL be saved when the application closes and SHALL show the keyword calls as groups.

#### Scenario: Trace of an application
- **WHEN** a test starts an application with `tracing` set to a `.zip` path, clicks in its window and closes it
- **THEN** the trace file exists, contains the click, and has a group for the `Click` keyword

#### Scenario: Tracing from the global setting
- **WHEN** `ROBOT_FRAMEWORK_BROWSER_TRACING` is `True` and a test starts and closes an application without `tracing`
- **THEN** a trace named after the application's context is in Browser's trace folder

#### Scenario: No tracing by default
- **WHEN** a test starts and closes an application without `tracing` and without the global setting
- **THEN** no trace is saved

### Requirement: HAR recording
`New Electron Application` SHALL record the network traffic of the application's windows into a HAR file when it is given `record_har`, with the keys of `recordHar` of Browser's `New Context`. A relative path SHALL be relative to the output directory. The file SHALL be written when the application closes.

#### Scenario: HAR of an application
- **WHEN** a test starts an application with `record_har`, loads a page from a web server in its window, makes the page fetch a resource and closes the application
- **THEN** the HAR file contains the request for the resource and its response

### Requirement: Downloads
Browser's `Download` SHALL work in an application's windows. The library SHALL give Browser the context options of the application, so that Browser knows that the application accepts downloads, as Electron does by default.

#### Scenario: Download in an application
- **WHEN** a window of an application shows a page from a web server and a test calls `Download` for a URL of that server
- **THEN** the file is saved with the content that the server returned

### Requirement: Keyword documentation
The library's own keywords SHALL document every argument, their return value and the exceptions they raise for invalid input, so that Libdoc shows them with the arguments, the return type and the exceptions.

#### Scenario: Keyword documentation
- **WHEN** libdoc generates the documentation of `Electron` or `Electron.Helper`
- **THEN** every argument of their own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it

### Requirement: Color scheme
`New Electron Application` SHALL leave the color scheme of the application's pages to the application by default, so that `prefers-color-scheme` reports what the application chose. When `color_scheme` is `light` or `dark`, the pages SHALL report that color scheme instead.

#### Scenario: Application decides the color scheme
- **WHEN** a test starts an application that switches its theme to dark, without `color_scheme`
- **THEN** its page matches `prefers-color-scheme: dark`

#### Scenario: Emulated color scheme
- **WHEN** a test starts the same application with `color_scheme=light`
- **THEN** its page matches `prefers-color-scheme: light`

### Requirement: Locale and time zone
`New Electron Application` SHALL start the application's pages with the given `locale` and `timezone_id`, which apply to the language the pages report and to their number and date formatting. Without them, the pages SHALL follow the system.

#### Scenario: Given locale and time zone
- **WHEN** a test starts an application with `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** its page reports the language `pt-BR` and the time zone `Asia/Tokyo`, and formats numbers as in Brazilian Portuguese

### Requirement: Bypass the Content Security Policy
`New Electron Application` SHALL start the application with the Content Security Policy of its pages bypassed, including Trusted Types, when `bypass_csp` is true. By default, the policy SHALL be enforced.

#### Scenario: Script added to a page with a strict policy
- **WHEN** a test starts an application whose page requires Trusted Types for scripts, with `bypass_csp=True`, and adds a script element with inline code through `Evaluate JavaScript`
- **THEN** the script runs

#### Scenario: Policy enforced by default
- **WHEN** the same test starts the application without `bypass_csp`
- **THEN** adding the script fails with an error about Trusted Types

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
