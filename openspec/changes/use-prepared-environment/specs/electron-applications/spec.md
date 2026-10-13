# Spec Delta

## MODIFIED Requirements

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
