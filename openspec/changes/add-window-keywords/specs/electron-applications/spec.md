## ADDED Requirements

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
The window keywords SHALL take a window as `title=<title>`, the exact title that it shows, or as its id from `Get Window Ids`, also without the prefix `window=`. For a title, they SHALL wait up to the library timeout until exactly one window of the active application shows it, and otherwise fail with an error that names the title and how many windows show it. For an id that is not a window of the active application, they SHALL fail with an error that names the id.

#### Scenario: Window that opens later
- **WHEN** a test clicks the fixture app's button that opens the second window and calls `Maximize Window    title=Second Window` right away
- **THEN** the keyword waits for the window and maximises it

#### Scenario: Id as a named argument
- **WHEN** a test passes the second window's id as the named argument `window=2`
- **THEN** the keyword acts on the second window

#### Scenario: Two windows with one title
- **WHEN** two windows show the title `Views` and a test calls `Maximize Window    title=Views`
- **THEN** the keyword fails after the library timeout with an error that names the title and says that two windows show it

#### Scenario: Unknown id
- **WHEN** a test calls `Get Window State` for an id that is not a window of the active application
- **THEN** the keyword fails with an error that names the id

### Requirement: Window of the size and state keywords
`Set Window Size`, `Get Window Size`, `Maximize Window`, `Minimize Window`, `Restore Window` and `Get Window State` SHALL act on the given window, or without one on the window that shows the active page, which for a view or `<webview>` is the window around it. They SHALL NOT change the active page.

#### Scenario: Window of the active view
- **WHEN** the page of a `WebContentsView` is the active page and a test calls `Maximize Window`
- **THEN** the window that shows the view is maximised

#### Scenario: Another window
- **WHEN** the first window is the active page and a test calls `Maximize Window` with the second window's id
- **THEN** the second window is maximised, and the first window's page is still the active page

### Requirement: Switch to a window
`Switch Window` SHALL make the own page of the given window the active page, also when views or `<webview>`s in the window load later, and SHALL return the id of the page that was active before. If other pages of the application have the same title as the window's own page, it SHALL fail with an error that names the title, and the active page SHALL stay the same.

#### Scenario: Switch by title and back
- **WHEN** the first window is the active page and a test calls `Switch Window    title=Second Window`, and then `Switch Window` with the id that it returned
- **THEN** the second window's page is the active page after the first call, and the first window's page after the second

#### Scenario: Switch by window id
- **WHEN** a test calls `Switch Window` with the second window's id from `Get Window Ids`
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

### Requirement: Switch to a page of a window
`Switch Window` SHALL also take a page id, as `Switch Page` does. If that page is a `WebContentsView` or `<webview>` and not a window's own page, it SHALL make the previous page active again and fail with an error that names the id.

#### Scenario: Page id of a window
- **WHEN** a test calls `Switch Window` with the page id that `Start Electron Application` returned
- **THEN** the first window's page is the active page

#### Scenario: Page of a view
- **WHEN** a test calls `Switch Window` with the page id of a `WebContentsView`
- **THEN** the keyword fails with an error that names the id, and the active page stays the same

### Requirement: Switch to a new window
With `NEW`, `Switch Window` SHALL make the newest page the active page, as `Switch Page    NEW` does, waiting for one within the library timeout. If the newest page is not a window's own page, it SHALL make the previous page active again and fail with an error that says so.

#### Scenario: Window opened by a click
- **WHEN** a test clicks the fixture app's button that opens a second window and calls `Switch Window    NEW`
- **THEN** the second window's page is the active page

#### Scenario: View newer than the new window
- **WHEN** the new window shows a `<webview>` whose page is newer than the window's own page, and a test calls `Switch Window    NEW`
- **THEN** the keyword fails with an error that says that the newest page is not a window, and the previous page is the active page

#### Scenario: No new page
- **WHEN** a test calls `Switch Window    NEW` and the application opens no window
- **THEN** the keyword fails after the library timeout with Browser's error that no new page opened

### Requirement: Set the window size
`Set Window Size` SHALL give the window the given content size, the size that the window's own page, its screenshots and its video have, and SHALL return once the window has that size, apart from the rounding of a fractional display scale. It SHALL restore a maximised or minimised window first.

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
`Maximize Window`, `Minimize Window` and `Restore Window` SHALL maximise the window, minimise it, or bring it back to its normal state from a maximised or minimised state, and SHALL return once the window is in that state.

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

### Requirement: Get the window state
`Get Window State` SHALL return `normal`, `maximized` or `minimized` for the window, also while the window is minimised. It SHALL take Browser's assertion operators and retry a failing assertion as Browser's getters do: for `retry_assertions_for`, within the library timeout.

#### Scenario: Started application
- **WHEN** an application has been started
- **THEN** `Get Window State    ==    normal` passes

#### Scenario: Minimised window
- **WHEN** the window that shows the active page is minimised
- **THEN** `Get Window State` returns `minimized`

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
