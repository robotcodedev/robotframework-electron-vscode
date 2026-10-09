# Spec Delta

## ADDED Requirements

### Requirement: Evaluate in the main process
`Evaluate In Main Process` SHALL run a JavaScript function in the main process of an application started by `New Electron Application`, the active one or the one with a given browser id. The function SHALL get the `electron` module and the keyword's `arg`, and the keyword SHALL return the function's result. For a browser that is not such an application, the keyword SHALL fail with a message that names it.

#### Scenario: Value from the main process
- **WHEN** a test evaluates `({ app }) => app.getName()` in the main process of the fixture app
- **THEN** the keyword returns the name from the fixture app's `package.json`

#### Scenario: Native dialog replaced
- **WHEN** a test replaces `dialog.showOpenDialog` in the main process with a function that returns a fixed path, and then clicks the fixture app's button that opens a file dialog
- **THEN** no dialog opens, and the page shows the fixed path

#### Scenario: Window sized from the main process
- **WHEN** a test sets the bounds of the fixture app's window to 1024×700 in the main process
- **THEN** the page's window is 1024×700

#### Scenario: Not an Electron application
- **WHEN** `Evaluate In Main Process` is called with a browser id that `New Electron Application` did not return
- **THEN** it fails with a message that names the browser id
