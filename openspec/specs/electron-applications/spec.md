# electron-applications Specification

## Purpose

Lets Robot Framework tests start Electron applications, drive their windows with the Browser library's keywords, and close the applications again, so that an Electron app can be tested like a web page.

## Requirements

### Requirement: Drop-in replacement for Browser
The `Electron` library SHALL provide every keyword of the Browser library it is built on, together with Browser's import arguments and their behaviour, in addition to its own keywords. It SHALL add no import arguments of its own.

#### Scenario: Browser keywords without Browser
- **WHEN** a suite imports `Electron` and does not import `Browser`
- **THEN** Browser keywords such as `New Page`, `Click` and `Get Text` can be called without a library prefix

#### Scenario: Browser import arguments
- **WHEN** a suite imports `Electron    timeout=5s    auto_closing_level=SUITE`
- **THEN** both settings take effect exactly as they do for `Browser    timeout=5s    auto_closing_level=SUITE`

### Requirement: Import starts nothing
Importing the `Electron` library, including generating its documentation or analysing it in an editor, SHALL NOT start the Playwright process or an application.

#### Scenario: Generating documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** no Node.js process and no application process is started

### Requirement: Library documentation
The library documentation SHALL describe the Electron keywords and SHALL contain the Browser library's documentation with working internal links. It SHALL report the version of the `Electron` library, not that of Browser.

#### Scenario: Generated documentation
- **WHEN** libdoc generates the documentation of `Electron`
- **THEN** it reports the version of `robotframework-electron`, and links in the Browser keyword documentation, such as those to `Assertions`, resolve to sections of the same document

### Requirement: Start an application
`New Electron Application` SHALL start the Electron application at a given executable path and SHALL return once the application's first window has opened. How long it waits for that window SHALL be configurable per call. Command-line arguments, a working directory and environment variables SHALL be passed to the application as given. If no environment variables are given, the application SHALL inherit the environment of the test run without `ELECTRON_RUN_AS_NODE`.

#### Scenario: Application opens a window
- **WHEN** `New Electron Application` is called with the path of an Electron application
- **THEN** the keyword returns after the application's first window has opened

#### Scenario: Arguments and environment
- **WHEN** the keyword is called with command-line arguments, a working directory and environment variables
- **THEN** the application receives these arguments, runs in that directory and sees exactly these environment variables

#### Scenario: Test run started from inside VS Code
- **WHEN** the test run has `ELECTRON_RUN_AS_NODE=1` in its environment, as runs started from VS Code do, and no environment variables are given
- **THEN** the application starts normally and does not see `ELECTRON_RUN_AS_NODE`

### Requirement: Windows are Browser pages
A started application SHALL be a browser in Browser's state with one context. Each of its windows SHALL be a page of that context, and its first window SHALL be the active page when `New Electron Application` returns.

#### Scenario: Browser keywords act on the first window
- **WHEN** an application has been started
- **THEN** `Get Title` returns the title of its first window and `Click` acts on that window

#### Scenario: Return value
- **WHEN** an application has been started
- **THEN** the keyword returns the browser id, the context id and the details of the first window's page, in the same form as `New Persistent Context`

### Requirement: Further windows
Windows that the application opens later SHALL become pages of its context without becoming the active page. Closing such a page SHALL close the window.

#### Scenario: Second window
- **WHEN** the application opens a second window
- **THEN** `Switch Page    NEW` makes that window the active page

#### Scenario: Closing a window
- **WHEN** `Close Page` is called while a window of the application is the active page
- **THEN** that window closes

### Requirement: Applications and browsers side by side
Each started application SHALL be a separate browser in Browser's state. Applications and ordinary browsers SHALL be usable in the same test, and `Switch Browser` SHALL switch between them.

#### Scenario: Application and web browser
- **WHEN** a test starts an application and then opens a web page with `New Browser` and `New Page`
- **THEN** `Switch Browser` with the application's browser id makes the application's window the active page again

### Requirement: Close an application
`Close Electron Application` SHALL end the active application, or the application whose browser id is given, and SHALL remove it from Browser's state. It SHALL return only after the application process has exited. It SHALL also succeed if the application has already exited.

#### Scenario: Close the active application
- **WHEN** `Close Electron Application` is called while an application is the active browser
- **THEN** the application process has exited when the keyword returns, and the browser that was active before becomes active again

#### Scenario: Close by browser id
- **WHEN** the keyword is called with the browser id of an application that is not the active browser
- **THEN** that application ends and the active browser stays active

#### Scenario: Application already exited
- **WHEN** the application has quit on its own and `Close Electron Application` is called
- **THEN** the keyword passes

### Requirement: Browser's closing ends the application
An application SHALL end whenever Browser closes its browser or context: through `Close Browser`, through `Close Context`, through automatic closing at the end of the test or suite that started it, and at the end of the run.

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
If the application cannot be started, or opens no window within the time allowed, `New Electron Application` SHALL fail with an error that names the cause. It SHALL leave no application process running and SHALL add nothing to Browser's state.

#### Scenario: Wrong executable path
- **WHEN** the executable path does not exist
- **THEN** the keyword fails with an error that names the path

#### Scenario: No window
- **WHEN** the application opens no window within the time allowed
- **THEN** the keyword fails, and afterwards no process of the application is running

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
