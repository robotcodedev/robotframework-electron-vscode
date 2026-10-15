---
title: Browser keywords in VS Code
description: Which Browser features need a setting or the main process in VS Code, and Browser keywords on the workbench.
sidebar:
  order: 5
---

VS Code is an Electron application, so everything in [Browser keywords in applications](../../electron/browser-keywords/) applies to it as well: which keywords work, which ones the libraries hide and why, such as [`Save Page As PDF`](../../electron/browser-keywords/#compared-with-the-browser-library), and where Electron behaves differently from a web browser. In addition:

| Feature | Status | Notes |
|---|---|---|
| `Evaluate JavaScript`, `Wait For Function` | Works | They run in the workbench's page, not in the extension host. |
| Copy and paste in the editor | Works | |
| A second window: `Switch Page    NEW`, `Close Page` | Works | See `windows.robot` in the example. |
| Locator handlers for notifications | Works | See below. |
| `Drag And Drop` in the explorer | Needs a setting | `explorer.confirmDragAndDrop: false`, otherwise VS Code asks for confirmation. |
| File dialogs | Needs a setting | `files.simpleDialog.enable: true` makes VS Code use its own dialog instead of the native one. |
| Native message boxes | Needs the main process | `Evaluate In Main Process` replaces `dialog.showMessageBox` before VS Code opens one. |
| `Record Selector` | Needs an option | `bypass_csp=True` of `Start VS Code`. The workbench requires Trusted Types for scripts, and the recorder adds a script to the page. |
| Maximised windows | Needs a window manager | See [CI and the Linux display](../../running/ci-and-display/). |

The example project uses many of these features. The following snippets show the others; they assume a VS Code started with `Start VS Code`.

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

Moving a file into a folder in the explorer, with `explorer.confirmDragAndDrop` set to `false` in the settings of `Start VS Code`:

```robotframework
Drag And Drop    .explorer-folders-view >> text="notes.txt"    .explorer-folders-view >> text="archive"
```

JavaScript coverage of the workbench while a command runs:

```robotframework
Start Coverage
Run Command    Robot Example: Say Hello
${report} =    Stop Coverage
```
