# Design

## Context

See proposal.md for motivation and specs/vscode-workbench/spec.md for the required behaviour. `add-vscode-launch` provides `Open VS Code`, which records the product version of each instance, and a plain JavaScript test extension. VS Code's own `test/automation/src/` drivers (`quickaccess.ts`, `quickinput.ts`, `editor.ts`, `notification.ts`) show how Microsoft drives the same UI and are the reference whenever VS Code changes.

## Goals / Non-Goals

**Goals:**
- A small set of reliable workbench keywords, built only on Browser keywords and one selector table.

**Non-Goals:**
- Executing commands by id or calling the `vscode` API. That would need a helper extension or main-process access, and can come later.
- Page objects for every view, such as the explorer, SCM or debug views. Add them when real tests need them.
- Reading lines the editor does not render.

## Decisions

### Keywords in a mixin

The workbench keywords live in `VSCode/workbench.py` as `@keyword` methods of a mixin class, and the library becomes `class VSCode(WorkbenchKeywords, Electron)`. A mixin keeps the module small and needs no registration, because robotlibcore collects `@keyword` methods from the class hierarchy.

### One selector table with version entries

- `VSCode/selectors.py` maps a selector name to a list of `(minimum_version, selector)` entries. The resolver picks the entry with the highest minimum version that is not above the running instance's version. Insiders builds count as their base version.
- `Set VS Code Selector` stores per-name overrides on the library instance. Overrides win over the table.
- Preferences: ARIA roles and labels before CSS classes, and stable workbench classes (`.quick-input-widget`, `.monaco-editor`, `.notifications-toasts`) before deep structural selectors.

### How each keyword works

- **`Execute VS Code Command`:**
  - Opens the palette with `F1` and types the title.
  - Waits for a list row whose label equals the title, then presses `Enter`.
  - Without an exact match, it presses `Escape` and fails.
- **`Open File In Editor`:**
  - Opens Quick Open with `ControlOrMeta+P` (Playwright maps it to Command on macOS) and types the relative path.
  - Picks the matching row.
  - Waits until the active tab shows the file name.
- **`Get Editor Text` / `Type In Editor`:**
  - Reading takes the active editor's `.view-lines` text, with non-breaking spaces normalised. It covers only the rendered lines; the keyword docs say so.
  - Typing focuses the editor's input area and uses `Keyboard Input    type`.
- **`Select Quick Pick Item`:** waits for a row with that label in the open quick input and clicks it.
- **`Get Notifications`:** returns the texts of the visible notification toasts.
- **`Enter Webview` / `Leave Webview`:**
  - Webviews are nested iframes. Entering sets Browser's selector prefix to the visible outer webview frame, filtered by `extensionId=<id>` in its `src` when an id is given, followed by its `#active-frame` (for example `iframe.webview.ready[src*="extensionId=robot.test-extension"] >>> iframe#active-frame >>>`).
  - It keeps the previous prefix that `Set Selector Prefix` returns. `Leave Webview` restores it.

### Test extension additions

The test extension from `add-vscode-launch` has the id `robot.test-extension` and gets three additions:
- `Robot Test: Say Hello` shows the notification `Hello Robot`.
- `Robot Test: Pick` shows a quick pick with `Alpha` and `Beta`, then a notification `Picked: <label>`.
- `Robot Test: Open Webview` opens a webview with a button and a text field that the button changes.

A small fixture workspace with `src/example.txt` and an empty file serves the editor tests.

## Risks / Trade-offs

- [Selectors break with new VS Code releases] → One table with version entries, `Set VS Code Selector` as an immediate workaround for users, and the `test/automation` drivers as the reference. Once CI exists, regular runs against stable, insiders and the oldest supported version.
- [Command titles depend on the display language] → Isolated instances start with VS Code's default English UI, and no language packs are installed unless a test adds them.
- [`Get Editor Text` sees only rendered lines] → Document it. Tests can scroll or open small files. Full text access can come later through a helper extension.
- [Webview frames are swapped on reload or theme change] → Selectors target `#active-frame` and are resolved again on every Browser call, and Browser's auto-waiting covers the swap.
