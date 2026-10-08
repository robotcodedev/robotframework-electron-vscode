# Design

## Context

See proposal.md for motivation and specs/vscode-examples/spec.md for the requirements. The VSCode library opens isolated instances (`Open VS Code`, `Close VS Code`), and `VSCode.Helper` provides executables. Everything shown in the workbench is reachable with plain Browser keywords. The findings from `add-vscode-launch` apply here:
- The command palette filters asynchronously, so pressing Enter right after typing can run the wrong command.
- Webviews are nested iframes.
- RobotCode runs from the root given with `-r` and changes into it, so `${EXECDIR}` is that root.

## Goals / Non-Goals

**Goals:**
- A copyable example that shows the patterns a project needs: its own keywords, locators as variables, profiles per VS Code version.
- The example is verified by running it.

**Non-Goals:**
- Covering many workbench parts. The example shows the patterns on four typical tasks; editors, the explorer or debugging follow the same way in a project.
- Keywords or resource files in the packages.

## Decisions

### Layout of the example

```
examples/vscode-extension/
  package.json, extension.js        extension "robot.example-extension": Say Hello, Pick, Open Webview
  robot.toml                         paths, output dir, profiles
  tests/
    resources/workbench.resource     keywords and locator variables
    resources/variables.resource     VS Code version, executable, cache
    commands.robot                   command palette
    quick_pick.robot                 quick pick and notifications
    webview.robot                    webview
  README.md
```

- **The extension** is plain JavaScript with no build step, like the test extension of the library. Its commands:
  - `Say Hello` shows a notification.
  - `Pick` shows a quick pick and then a notification that names the item.
  - `Open Webview` opens a webview with a button that changes a text.
- **Running:** The project is run with `uv run robotcode -r examples/vscode-extension robot` from the repository root. A user runs it from the copied folder with `robotcode robot`. Both use the example's own `robot.toml`, and `${EXECDIR}` is the example's root in both cases. All paths in the example are built from `${EXECDIR}`, so it refers to nothing outside its folder.
- **VS Code version:** `${VSCODE_VERSION}` is a fixed version, initially 1.141.0. `${VSCODE_EXECUTABLE}` and `${VSCODE_CACHE}` default to `${NONE}`, so a copied project downloads into the user's cache like any user project.

### Keywords of the example

All keywords are user keywords that use only Browser keywords and the library's `Open VS Code`.
- **`Run Command    ${title}`:** `F1`, type the title, wait for the row whose `aria-label` contains the title, press `Enter`.
- **`Select Quick Pick Item    ${label}`:** wait for the row with that label, then click it.
- **`Notification Should Be Shown    ${message}`:** wait until a notification toast shows the text.
- **`Enter Webview    ${extension_id}`:** sets Browser's selector prefix to the extension's webview frames (`iframe.webview.ready[src*="extensionId=…"] >>> iframe#active-frame >>>`) and returns the previous prefix. **`Leave Webview    ${previous}`** restores it. The previous prefix travels as a return value and an argument, not as a suite or global variable.

The frame selectors of the webview are checked against VS Code 1.141 while the example is written.

### Locators and profiles

- Every locator is a variable in `workbench.resource` (for example `${COMMAND_PALETTE_ROW}`, `${NOTIFICATION_MESSAGE}`, `${WEBVIEW_FRAMES}`).
- The example's `robot.toml` has a profile that overrides one locator with an equivalent selector. It shows the mechanism and is used to test it.
- Its comments explain that real projects add one profile per VS Code version whose locators differ.

### Repository integration

- The examples are not part of the root `robot.toml` paths: they have their own project root and configuration.
- AGENTS.md lists the command for running them next to the library tests.
- The README of `robotframework-vscode` gets a short section that points to the example and names the important points (own keywords, locators as variables, profiles per version, waiting in the command palette, webview frames).

### Library cleanup

- `VSCode` drops `VSCodeInstance` and the instance registry, which only existed to choose version-specific locators.
- A pytest test pins the boundary from the spec: the only keywords `VSCode` adds to those of `Electron` are `Open VS Code` and `Close VS Code`.

## Risks / Trade-offs

- [The example's locators break with a new VS Code release] → That is exactly what the example run shows. The fix then lands in the example, and users see how to adapt their own locators.
- [Users copy the example and never update it] → Expected. The library promises no locators, and the README says so.
- [The first example run downloads VS Code into the user's cache] → Needed once per version, as for any user project. Local runs can set `VSCODE_CACHE` or `VSCODE_EXECUTABLE` in a personal `.robot.toml` inside the example folder.
