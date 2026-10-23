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
`Start Electron Application` SHALL start the Electron application at a given executable path, or a command on `PATH`, and SHALL return once the application's first window has opened. How long it waits for that window SHALL be configurable per call. Command-line arguments, a working directory and environment variables SHALL be passed to the application as given. A relative executable path and a relative working directory SHALL be relative to the test run's working directory, and without a working directory the application SHALL run in the test run's working directory. If no environment variables are given, the application SHALL inherit the environment of the test run without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Application opens a window
- **WHEN** `Start Electron Application` is called with the path of an Electron application
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
A started application SHALL be a browser in Browser's state with one context. Each of its windows SHALL be a page of that context, and its first window SHALL be the active page when `Start Electron Application` returns, also when the application shows `WebContentsView`s or `<webview>`s, which are pages of the context as well.

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
If the application cannot be started, opens no window within the time allowed, or cannot be taken over by the Browser library, `Start Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state.

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
`Start Electron Application` SHALL record a video of the application's windows when it is given `record_video`. It SHALL store the video in Browser's video folder of the output directory unless `record_video` names a folder, return the video's path in the page details of its return value, and embed the video in the log, as Browser does for `New Context`.

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
`Start Electron Application` SHALL record a Playwright trace of the application when it is given `tracing`, with the values and paths of `tracing` of Browser's `New Context`, and also when the variable or environment variable `ROBOT_FRAMEWORK_BROWSER_TRACING` is `True`. The trace SHALL be saved when the application closes and SHALL show the keyword calls as groups.

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
`Start Electron Application` SHALL record the network traffic of the application's windows into a HAR file when it is given `record_har`, with the keys of `recordHar` of Browser's `New Context`. A relative path SHALL be relative to the output directory. The file SHALL be written when the application closes.

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
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** every argument of its own keywords has a description, keywords that return a value document it, and keywords that raise an exception for invalid input document it

### Requirement: Color scheme
`Start Electron Application` SHALL leave the color scheme of the application's pages to the application by default, so that `prefers-color-scheme` reports what the application chose. When `color_scheme` is `light` or `dark`, the pages SHALL report that color scheme instead.

#### Scenario: Application decides the color scheme
- **WHEN** a test starts an application that switches its theme to dark, without `color_scheme`
- **THEN** its page matches `prefers-color-scheme: dark`

#### Scenario: Emulated color scheme
- **WHEN** a test starts the same application with `color_scheme=light`
- **THEN** its page matches `prefers-color-scheme: light`

### Requirement: Locale and time zone
`Start Electron Application` SHALL start the application's pages with the given `locale` and `timezone_id`, which apply to the language the pages report and to their number and date formatting. Without them, the pages SHALL follow the system.

#### Scenario: Given locale and time zone
- **WHEN** a test starts an application with `locale=pt-BR` and `timezone_id=Asia/Tokyo`
- **THEN** its page reports the language `pt-BR` and the time zone `Asia/Tokyo`, and formats numbers as in Brazilian Portuguese

### Requirement: Bypass the Content Security Policy
`Start Electron Application` SHALL start the application with the Content Security Policy of its pages bypassed, including Trusted Types, when `bypass_csp` is true. By default, the policy SHALL be enforced.

#### Scenario: Script added to a page with a strict policy
- **WHEN** a test starts an application whose page requires Trusted Types for scripts, with `bypass_csp=True`, and adds a script element with inline code through `Evaluate JavaScript`
- **THEN** the script runs

#### Scenario: Policy enforced by default
- **WHEN** the same test starts the application without `bypass_csp`
- **THEN** adding the script fails with an error about Trusted Types

### Requirement: Evaluate in the main process
`Evaluate In Main Process` SHALL run a JavaScript function in the main process of an application started by `Start Electron Application`, the active one or the one with a given application id. The function SHALL be a required argument; further arguments continue it. It SHALL get the `electron` module and the keyword's `arg`, and the keyword SHALL return the function's result. Without an open application, or for an id that is not such an application, it SHALL fail with a message that says so.

#### Scenario: Value from the main process
- **WHEN** a test evaluates `({ app }) => app.getName()` in the main process of the fixture app
- **THEN** the keyword returns the name from the fixture app's `package.json`

#### Scenario: Native dialog replaced
- **WHEN** a test replaces `dialog.showOpenDialog` in the main process with a function that returns a fixed path, and then clicks the fixture app's button that opens a file dialog
- **THEN** no dialog opens, and the page shows the fixed path

#### Scenario: Not an Electron application
- **WHEN** `Evaluate In Main Process` is called with an application id that `Start Electron Application` did not return
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

### Requirement: Window ids
`Get Window Ids` SHALL return the ids of the active application's windows, which are its `BrowserWindow`s, so that `WebContentsView`s and `<webview>`s are not among them, in the order in which the windows opened. The ids SHALL be valid while the application runs. With `ACTIVE`, the list SHALL hold only the id of the window that shows the active page. It SHALL change neither the active page nor which window has the focus.

#### Scenario: Windows of an application
- **WHEN** the fixture app has opened its second window
- **THEN** `Get Window Ids` returns two ids

#### Scenario: Views are not windows
- **WHEN** the fixture app shows a `WebContentsView` and a `<webview>` in its window
- **THEN** `Get Window Ids` returns one id

#### Scenario: Window of the active view
- **WHEN** the page of a `WebContentsView` is the active page
- **THEN** `Get Window Ids    ACTIVE` returns a list with the id of the window that shows the view

#### Scenario: Active page and focus unchanged
- **WHEN** the second window is the active page and has the focus, and a test calls `Get Window Ids`
- **THEN** the second window is still the active page and still has the focus

### Requirement: Window titles
`Get Window Titles` SHALL return the titles that the active application's windows show, in the order of `Get Window Ids`, also where the application sets a window's title itself. It SHALL change neither the active page nor which window has the focus.

#### Scenario: Titles of two windows
- **WHEN** the fixture app has opened its second window
- **THEN** `Get Window Titles` returns `Electron Fixture` and `Second Window`

#### Scenario: Title set by the application
- **WHEN** the application shows the title `Native Title` in a window whose page has the title `Page Title`
- **THEN** `Get Window Titles` returns `Native Title` for that window

### Requirement: Giving a window
The window keywords SHALL take a window as `title=<title>`, the exact title that it shows, as `title=/<pattern>/<flags>`, a JavaScript regular expression that its title matches, or as its id from `Get Window Ids`, also without the prefix `window=`. For an id that is not a window of the active application, they SHALL fail with an error that names the id.

#### Scenario: Title as a regular expression
- **WHEN** the fixture app has opened its second window and a test calls `Maximize Window    title=/^second WINDOW$/i`
- **THEN** the second window is maximised

#### Scenario: Id as a named argument
- **WHEN** a test passes the second window's id as the named argument `window=2`
- **THEN** the keyword acts on the second window

#### Scenario: Unknown id
- **WHEN** a test calls `Get Window State` for an id that is not a window of the active application
- **THEN** the keyword fails with an error that names the id

### Requirement: Waiting for a window by its title
For a title or a regular expression, the window keywords SHALL wait up to the library timeout until exactly one window of the active application matches, and otherwise fail with an error that names the title or the expression and how many windows match.

#### Scenario: Window that opens later
- **WHEN** a test clicks the fixture app's button that opens the second window and calls `Maximize Window    title=Second Window` right away
- **THEN** the keyword waits for the window and maximises it

#### Scenario: Two windows with one title
- **WHEN** two windows show the title `Views` and a test calls `Maximize Window    title=Views`
- **THEN** the keyword fails after the library timeout with an error that names the title and says that two windows show it

#### Scenario: Expression that matches two windows
- **WHEN** the fixture app's windows show `Electron Fixture` and `Second Window`, and a test calls `Maximize Window    title=/o/`
- **THEN** the keyword fails after the library timeout with an error that names the expression and says that two windows match it

### Requirement: Window of the size and state keywords
`Set Window Size`, `Get Window Size`, `Maximize Window`, `Minimize Window`, `Restore Window` and `Get Window State` SHALL act on the given window, or without one on the window that shows the active page, which for a view or `<webview>` is the window around it. They SHALL NOT change the active page.

#### Scenario: Window of the active view
- **WHEN** the page of a `WebContentsView` is the active page and a test calls `Maximize Window`
- **THEN** the window that shows the view is maximised

#### Scenario: Another window
- **WHEN** the first window is the active page and a test calls `Maximize Window` with the second window's id
- **THEN** the second window is maximised, and the first window's page is still the active page

### Requirement: Switch to a window
`Switch Window` SHALL make the own page of the given window the active page, also when views or `<webview>`s in the window load later, and SHALL return the id of the page that was active before. If the window's own page has no title, or other pages of the application have the same title, it SHALL fail with an error that says so and points to switching by page id, and the active page SHALL stay the same.

#### Scenario: Switch by title and back
- **WHEN** the first window is the active page and a test calls `Switch Window    title=Second Window`, and then `Switch Window` with the id that it returned
- **THEN** the second window's page is the active page after the first call, and the first window's page after the second

#### Scenario: Switch by window id
- **WHEN** a test calls `Switch Window` with the second window's id from `Get Window Ids`
- **THEN** the second window's page is the active page

#### Scenario: Switch by a regular expression
- **WHEN** the fixture app has opened its second window and a test calls `Switch Window    title=/^Second/`
- **THEN** the second window's page is the active page

#### Scenario: Window whose webview loads later
- **WHEN** a window shows a `<webview>` that loads after the window, and a test calls `Switch Window` with the window's title
- **THEN** the window's own page is the active page

#### Scenario: Title set by the application
- **WHEN** a window shows the title `Native Title`, its page has the title `Page Title`, and a test calls `Switch Window    title=Native Title`
- **THEN** that window's own page is the active page

#### Scenario: Pages with one title
- **WHEN** the pages of two windows both have the title `Views` and a test calls `Switch Window` with the id of one of the windows
- **THEN** the keyword fails with an error that names the title, and the active page stays the same

#### Scenario: Page without a title
- **WHEN** a window shows a page that has no title and a test calls `Switch Window` with the window's id
- **THEN** the keyword fails after the library timeout with an error that says that the page has no title, and the active page stays the same

### Requirement: Switch to a page of a window
`Switch Window` SHALL also take a page id, as `Switch Page` does. If that page is a `WebContentsView` or `<webview>` and not a window's own page, it SHALL make the previous page active again and fail with an error that names the id.

#### Scenario: Page id of a window
- **WHEN** a test calls `Switch Window` with the page id that `Start Electron Application` returned
- **THEN** the first window's page is the active page

#### Scenario: Page of a view
- **WHEN** a test calls `Switch Window` with the page id of a `WebContentsView`
- **THEN** the keyword fails with an error that names the id, and the active page stays the same

#### Scenario: Page of another application
- **WHEN** two applications are open and a test calls `Switch Window` with the page id of a window of the application that is not active
- **THEN** that application is the active one, and its window's page is the active page, as with `Switch Page`

### Requirement: Switch to a new window
With `NEW`, in any letter case, `Switch Window` SHALL make the newest page the active page, as `Switch Page    NEW` does, waiting for one within the library timeout. If the newest page is not a window's own page, it SHALL make the previous page active again and fail with an error that says so.

#### Scenario: Window opened by a click
- **WHEN** a test clicks the fixture app's button that opens a second window and calls `Switch Window    new`
- **THEN** the second window's page is the active page

#### Scenario: View newer than the new window
- **WHEN** the new window shows a `<webview>` whose page is newer than the window's own page, and a test calls `Switch Window    NEW`
- **THEN** the keyword fails with an error that says that the newest page is not a window, and the previous page is the active page

#### Scenario: No new page
- **WHEN** a test calls `Switch Window    NEW` and the application opens no window
- **THEN** the keyword fails after the library timeout with Browser's error that no new page opened

### Requirement: Set the window size
`Set Window Size` SHALL give the window the given content size, the size that the window's own page, its screenshots and its video have, and SHALL return once the window has that size, apart from the rounding of a fractional display scale. It SHALL bring a maximised, minimised or fullscreen window back to its normal state first.

#### Scenario: Size of a window
- **WHEN** a test calls `Set Window Size    1024    700`
- **THEN** the window's own page is 1024 pixels wide and 700 pixels high

#### Scenario: Maximised window
- **WHEN** the window is maximised and a test calls `Set Window Size    1024    700`
- **THEN** `Get Window State` returns `normal`, and the window has that size

### Requirement: Get the window size
`Get Window Size` SHALL return the content size of the window as a dictionary with `width` and `height`, or only one of them when it is given as key. It SHALL take Browser's assertion operators and retry a failing assertion as Browser's getters do: for `retry_assertions_for`, within the library timeout.

#### Scenario: Size after setting it
- **WHEN** a test has called `Set Window Size    1024    700`
- **THEN** `Get Window Size` returns `{"width": 1024, "height": 700}`, and `Get Window Size    width    ==    1024` passes

#### Scenario: Failing assertion
- **WHEN** a test calls `Get Window Size    width    ==    1` on a window that is wider
- **THEN** the keyword fails once `retry_assertions_for` is over, with Browser's assertion message

### Requirement: Change the window state
`Maximize Window`, `Minimize Window` and `Restore Window` SHALL maximise the window, minimise it, or bring it back to its normal state from a maximised, minimised or fullscreen state, and SHALL return once the window is in that state and stays there.

#### Scenario: Maximise
- **WHEN** a test calls `Maximize Window`
- **THEN** `Get Window State` returns `maximized`, and the window is larger than before

#### Scenario: Minimise and restore
- **WHEN** a test calls `Minimize Window` and then `Restore Window`
- **THEN** `Get Window State` returns `minimized` after the first keyword and `normal` after the second, and the window has its size from before

#### Scenario: Restore a maximised window
- **WHEN** a test maximises a window and then calls `Restore Window`
- **THEN** `Get Window State` returns `normal`, and the window has its size from before

#### Scenario: Restore a window that was maximised before it was minimised
- **WHEN** a test maximises a window, minimises it and then calls `Restore Window`
- **THEN** `Get Window State` returns `normal`

#### Scenario: Restore a fullscreen window
- **WHEN** the application has put its window into fullscreen and a test calls `Restore Window`
- **THEN** the window has left fullscreen, and `Get Window State` returns `normal`

### Requirement: Get the window state
`Get Window State` SHALL return `normal`, `maximized` or `minimized` for the window, also while the window is minimised, and `maximized` for a fullscreen window, which fills the screen as well. It SHALL take Browser's assertion operators and retry a failing assertion as Browser's getters do: for `retry_assertions_for`, within the library timeout.

#### Scenario: Started application
- **WHEN** an application has been started
- **THEN** `Get Window State    ==    normal` passes

#### Scenario: Minimised window
- **WHEN** the window that shows the active page is minimised
- **THEN** `Get Window State` returns `minimized`

#### Scenario: Fullscreen window
- **WHEN** the application has put the window that shows the active page into fullscreen
- **THEN** `Get Window State` returns `maximized`

### Requirement: Window changes that do not happen
If the window does not reach the requested size or state within the library timeout, the keyword SHALL fail with an error that names the requested and the actual size or state, and the likely cause: a display without a window manager, or a desktop that cannot apply the change, such as one that cannot minimise windows.

#### Scenario: Display without a window manager
- **WHEN** a test calls `Maximize Window` for a window on a display without a window manager
- **THEN** the keyword fails after the library timeout with an error that names the requested state `maximized`, the actual state `normal`, and a missing window manager as the likely cause

### Requirement: Window keywords need an application
The window keywords SHALL act on the active application. Without an open application, they SHALL fail with "No application is open."

#### Scenario: No application open
- **WHEN** no application is open and a test calls `Maximize Window`
- **THEN** the keyword fails with "No application is open."

### Requirement: Guide on windows
The guide on Browser keywords SHALL explain how windows and pages relate, that window keywords take a window's title or its id, which is unique only within its application, that `Switch Window` takes page ids as well and `Switch Page` selects views and `<webview>`s, and that a new window is best selected by its title, because `NEW` takes the newest page, which can be a view or a page that was open before.

#### Scenario: Switching to a new window
- **WHEN** someone looks up in the guide how to switch to a window that the application opens
- **THEN** the guide shows `Switch Window` with the window's title and explains why `NEW` can select a view or a page that was open before

### Requirement: Guide on window states
The guide on Browser keywords SHALL explain that a minimised window draws nothing until it is restored, so that Browser keywords on it wait until their timeout, and which displays can maximise and minimise windows.

#### Scenario: Maximising on CI
- **WHEN** someone looks up in the guide how to maximise a window in a test that runs on CI
- **THEN** the guide shows `Maximize Window` and says that the display needs a window manager, which the display profiles start
