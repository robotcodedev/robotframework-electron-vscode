# Spec Delta

## Purpose

Keywords that drive the VS Code workbench in tests: running commands, opening files, working with the editor, quick picks and notifications, and acting inside extension webviews. Their selectors are kept in one place so that they can follow VS Code releases.

## ADDED Requirements

### Requirement: Run a command
`Execute VS Code Command` SHALL run the command with the given title through the command palette. It SHALL fail if no command with exactly that title exists.

#### Scenario: Extension command
- **WHEN** `Execute VS Code Command    Robot Test: Say Hello` is called with the test extension loaded
- **THEN** the extension's notification appears

#### Scenario: Unknown command
- **WHEN** the keyword is called with a title that matches no command
- **THEN** the keyword fails with an error that names the title, and the command palette is closed

### Requirement: Open a file
`Open File In Editor` SHALL open a file of the workspace by its relative path through Quick Open and SHALL return once the file is the active editor.

#### Scenario: File becomes active editor
- **WHEN** `Open File In Editor    src/example.txt` is called in a workspace that contains this file
- **THEN** the active editor tab shows `example.txt`

### Requirement: Read and type editor text
`Get Editor Text` SHALL return the text of the lines that the active editor currently shows. `Type In Editor` SHALL type the given text at the cursor of the active editor.

#### Scenario: Typed text can be read
- **WHEN** `Type In Editor    hello robot` is called in an empty file
- **THEN** `Get Editor Text` returns `hello robot`

### Requirement: Quick picks
`Select Quick Pick Item` SHALL select the item with the given label in the open quick pick. It SHALL fail if no item has that label.

#### Scenario: Item is selected
- **WHEN** an extension shows a quick pick with the items `Alpha` and `Beta`, and `Select Quick Pick Item    Beta` is called
- **THEN** the extension receives `Beta` as the selection

### Requirement: Notifications
`Get Notifications` SHALL return the messages of the notifications currently shown, newest first.

#### Scenario: Notification message
- **WHEN** the test extension has shown the notification `Hello Robot`
- **THEN** `Get Notifications` returns a list that contains `Hello Robot`

### Requirement: Act inside webviews
`Enter Webview` SHALL make Browser keywords act inside a visible extension webview, optionally selected by extension identifier, until `Leave Webview` restores the previous selector prefix.

#### Scenario: Click inside a webview
- **WHEN** the test extension's webview is open and `Enter Webview    robot.test-extension` is called
- **THEN** `Click` and `Get Text` act on elements inside the webview

#### Scenario: Leave the webview
- **WHEN** `Leave Webview` is called
- **THEN** Browser keywords act on the workbench again

### Requirement: Selectors follow VS Code versions
The workbench keywords SHALL take their selectors from one table that holds version-specific entries, and SHALL use the entry that matches the running VS Code version. `Set VS Code Selector` SHALL override a selector by name for the rest of the run.

#### Scenario: Override a selector
- **WHEN** `Set VS Code Selector    notification.message    <selector>` is called
- **THEN** `Get Notifications` uses that selector

### Requirement: Platform-independent shortcuts
Keyboard shortcuts used by the workbench keywords SHALL work on Linux, Windows and macOS, using Command on macOS where VS Code does.

#### Scenario: Quick Open on macOS
- **WHEN** `Open File In Editor` runs on macOS
- **THEN** Quick Open is opened with Command+P
