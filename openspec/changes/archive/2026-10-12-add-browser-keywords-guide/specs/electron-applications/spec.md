# Spec Delta

## ADDED Requirements

### Requirement: Browser keywords on application windows
Browser's keywords for locating elements, reading and input, waiting, context state, dialogs and downloads SHALL work on the windows of an application as they do on the pages of a web browser. Pages without a window of their own, such as `<webview>` guests and `WebContentsView`s, SHALL be selectable by their page id.

#### Scenario: Locators in a window
- **WHEN** a test locates elements in a window of the fixture app with CSS, XPath, text, id, role and test id selectors, through a shadow root, and in an iframe with `>>>`
- **THEN** each selector finds its element

#### Scenario: Context state
- **WHEN** a test adds a cookie and an entry in local storage in a window of the fixture app
- **THEN** `Get Cookie` and `LocalStorage Get Item` return them

#### Scenario: Dialogs
- **WHEN** a test accepts an `alert` and a `confirm` of the fixture app with `Handle Future Dialogs`
- **THEN** the page sees the confirmation

#### Scenario: Download after a click
- **WHEN** a test clicks a download link in the fixture app with `Promise To Wait For Download`
- **THEN** the downloaded file is saved where the test asked

#### Scenario: Pages without a window
- **WHEN** the fixture app shows a `<webview>` and a `WebContentsView`
- **THEN** both are pages in `Get Browser Catalog`, and after `Switch Page` with their page ids, Browser keywords act on them

### Requirement: Guide on Browser keywords
The documentation site SHALL have a guide that says, for each group of Browser keywords, what works on an application, which keywords fail and why, and which behaviours of Electron tests need to know. For each keyword that the guide lists as failing, an acceptance test SHALL expect its error.

#### Scenario: A keyword that fails
- **WHEN** someone looks up `Save Page As PDF` in the guide
- **THEN** the guide says that it fails on applications and why

#### Scenario: A behaviour of Electron
- **WHEN** someone looks up why `Press Keys` does not trigger a menu item's accelerator
- **THEN** the guide explains it and shows how to click the menu item in the main process instead

#### Scenario: A limitation lifted by an upgrade
- **WHEN** a Browser or Playwright upgrade makes a keyword work that the guide lists as failing
- **THEN** the acceptance test for that keyword fails
