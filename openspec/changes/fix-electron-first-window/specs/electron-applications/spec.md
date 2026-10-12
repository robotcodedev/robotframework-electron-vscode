# Spec Delta

## MODIFIED Requirements

### Requirement: Windows are Browser pages
A started application SHALL be a browser in Browser's state with one context. Each of its windows SHALL be a page of that context, and its first window SHALL be the active page when `New Electron Application` returns, also when the application shows `WebContentsView`s or `<webview>`s, which are pages of the context as well.

#### Scenario: Browser keywords act on the first window
- **WHEN** an application has been started
- **THEN** `Get Title` returns the title of its first window and `Click` acts on that window

#### Scenario: Return value
- **WHEN** an application has been started
- **THEN** the keyword returns the browser id, the context id and the details of the first window's page, in the same form as `New Persistent Context`

#### Scenario: Views at the start
- **WHEN** an application shows a `WebContentsView` and a `<webview>` in its first window when it starts
- **THEN** the window's own page is the active page, and the returned page details are those of that page
