---
title: Browser features in VS Code
description: Which Browser library features work with VS Code and Electron applications, which need a setting, and which do not work.
---

VS Code's windows are ordinary Browser pages, so most Browser keywords work on them. These results come from VS Code 1.141 under Xvfb, with Browser on Playwright 1.63. Most of them apply to other Electron applications as well.

## Overview

| Feature | Status | Notes |
|---|---|---|
| `Take Screenshot` of the window or an element, screenshots on failure | Works | Screenshots have the window's size. |
| Videos (`record_video`) | Works | See [Videos and slow motion](../videos/). |
| `Get Aria Snapshot`, role selectors such as `Get Element By Role` | Works | Useful to find locators. |
| `Evaluate JavaScript`, `Wait For Function` | Works | They run in the workbench's page, not in the extension host. |
| Keyboard, mouse and `Hover` keywords | Works | Shortcuts with `ControlOrMeta` work on every platform. |
| Copy and paste in the editor | Works | |
| `Get Console Log`, `Get Page Errors` | Works | The workbench's console messages. |
| `Highlight Elements`, `Set Presenter Mode` | Works | Presenter mode also serves as slow motion. |
| A second window: `Switch Page    NEW`, `Close Page` | Works | See `windows.robot` in the example. |
| Locator handlers (`Add Locator Handler Custom`) | Works | See below. |
| `Start Coverage`, `Stop Coverage` | Works | JavaScript coverage of the workbench. |
| `Set Viewport Size` | Works | It emulates the size; `Get Viewport Size` returns nothing before it is set. |
| `Drag And Drop` in the explorer | Needs a setting | `explorer.confirmDragAndDrop: false`, otherwise VS Code asks for confirmation. |
| File dialogs | Needs a setting | `files.simpleDialog.enable: true` makes VS Code use its own dialog. |
| Maximised windows | Needs a window manager | See [CI and the Linux display](../ci-and-display/). |
| Native dialogs and message boxes | Does not work | They are outside the page. |
| `Save Page As PDF` | Does not work | Electron does not provide Chromium's PDF printing (`Page.printToPDF`). |
| Playwright's `slowMo` | Does not work | Playwright has no `slowMo` for Electron; use presenter mode. |
| Tracing and HAR recording | Works | `tracing` and `record_har` of `New Electron Application` and `Open VS Code`, see [Traces and HAR files](../traces/). |
| `Download` | Works | Tested with an Electron application. The libraries tell Browser that the application accepts downloads, as Electron does by default. |

## Snippets

The example project uses many of these features. The following snippets show the others; they assume a VS Code opened with `Open VS Code`.

An aria snapshot of a part of the workbench lists its roles and names:

```robotframework
${snapshot} =    Get Aria Snapshot    .activitybar
```

The workbench's console messages and page errors:

```robotframework
${messages} =    Get Console Log
${errors} =    Get Page Errors
```

A locator handler closes notifications before every Browser action. The close button of a notification is shown only when the notification is in focus, so the handler first clicks the message and then the button:

```robotframework
Add Locator Handler Custom    .notifications-toasts .notification-toast
...    ${{ [{"action": "click", "selector": ".notifications-toasts .notification-list-item-message"}, {"action": "click", "selector": ".notifications-toasts .notification-toast .codicon-notifications-clear"}] }}
```

Moving a file into a folder in the explorer, with `explorer.confirmDragAndDrop` set to `false` in the settings of `Open VS Code`:

```robotframework
Drag And Drop    .explorer-folders-view >> text="notes.txt"    .explorer-folders-view >> text="archive"
```

JavaScript coverage of the workbench while a command runs:

```robotframework
Start Coverage
Run Command    Robot Example: Say Hello
${report} =    Stop Coverage
```

Downloading a file into the output directory from a page of an Electron application. The page must be loaded from a URL, and `Download` fetches the file from that page:

```robotframework
Go To    https://example.com/
${download} =    Download    https://example.com/report.csv    saveAs=${OUTPUT_DIR}/report.csv
```
