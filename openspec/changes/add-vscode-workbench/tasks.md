# Tasks

## 1. Selector table

- [ ] 1.1 Create `VSCode/selectors.py` with the version-entry table and the resolver, and add `Set VS Code Selector`. Verify with pytest that the resolver picks the right entry for older, newer and insiders versions, and that overrides win.
- [ ] 1.2 Create `VSCode/workbench.py` with the `WorkbenchKeywords` mixin, and make `VSCode` inherit from it. Verify with pytest that libdoc lists the new keywords.

## 2. Test fixtures

- [ ] 2.1 Extend the test extension (`robot.test-extension`) with `Robot Test: Pick` and `Robot Test: Open Webview`, and make `Say Hello` show `Hello Robot`. Verify by running the commands manually in an instance opened with `Open VS Code`.
- [ ] 2.2 Add a fixture workspace with `src/example.txt` and an empty file. Verify that `Open VS Code` opens it as workspace.

## 3. Commands, files and notifications

- [ ] 3.1 Implement `Execute VS Code Command`. Verify with Robot tests for "Extension command" and "Unknown command".
- [ ] 3.2 Implement `Get Notifications`. Verify with Robot tests for "Notification message" and "Override a selector".
- [ ] 3.3 Implement `Open File In Editor` with `ControlOrMeta+P`. Verify with a Robot test for "File becomes active editor".

## 4. Editor and quick picks

- [ ] 4.1 Implement `Get Editor Text` and `Type In Editor`, and document the rendered-lines limitation. Verify with a Robot test for "Typed text can be read".
- [ ] 4.2 Implement `Select Quick Pick Item`. Verify with a Robot test for "Item is selected".

## 5. Webviews

- [ ] 5.1 Implement `Enter Webview` and `Leave Webview` on top of `Set Selector Prefix`. Check the frame selectors against the current stable VS Code. Verify with Robot tests for "Click inside a webview" and "Leave the webview".

## 6. Documentation

- [ ] 6.1 Write the keyword docs and a README section about the selector table, `Set VS Code Selector` and how to update selectors with VS Code's `test/automation` drivers. Verify that libdoc shows all workbench keywords with their docs.
