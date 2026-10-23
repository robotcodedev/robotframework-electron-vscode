---
title: Browser keywords in applications
description: Which Browser keywords work on Electron applications, which fail and why, and what Electron does differently from a web browser.
sidebar:
  order: 2
---

`Electron` and `VSCode` contain the Browser keywords that apply to applications. They work on an application's windows as they do on the pages of a web browser. This guide lists, for each group of keywords, what works, which keywords the libraries hide and why, which keywords fail, and where Electron behaves differently.

The results come from Electron 44.7 and VS Code 1.141 under Xvfb, with Browser on Playwright 1.63. The acceptance tests in `packages/electron/atest/browser_keywords/` check the groups of the overview on an Electron application, except the row "Other keywords", and every keyword that this guide lists as failing.

## How an application looks to Browser

- **One browser, one context.** `Start Electron Application` and `Start VS Code` make the application a browser with one context. Each window of the application is a page of that context, and so are its `<webview>`s and `WebContentsView`s.
- **The application creates its pages.** The libraries hide `New Page`, `New Context` and the other keywords for browsers and contexts, and offer keywords for applications instead, see [Compared with the Browser library](#compared-with-the-browser-library).
- **Settings mean a restart.** Options such as the color scheme or the locale apply from the start, see [launch options](../getting-started/#launch-options). Another value means starting the application again.
- **The main process is outside the pages.** Native dialogs, menus and the tray belong to the main process, which Browser keywords do not reach. `Evaluate In Main Process` runs code there, see [the main process](../getting-started/#the-main-process).

## Overview

| Group | Status | Notes |
|---|---|---|
| Locators | Works | CSS, XPath, text, `id=`, `data-testid=`, `role=`, `Get Element By` and chains with `>>`, also through shadow roots and into iframes with `>>>`. See [Locators](#locators). |
| Reading content | Works | `Get Text`, `Get Attribute`, `Get Property`, `Get Style`, the table keywords, `Evaluate JavaScript`, `Get Console Log` and `Get Page Errors`. `Get Aria Snapshot` lists roles and names, which helps to find locators. |
| Input | Works | Typing, `Fill Secret`, checkboxes and selects, file uploads with `Upload File By Selector` and `Promise To Upload File`, keyboard, mouse, `Drag And Drop` and scrolling. Shortcuts with `ControlOrMeta` work on every platform, but they reach only the page, not the application's menu, see [Shortcuts and menus](#shortcuts-and-menus). |
| Waiting and navigation | Works | `Wait For Elements State`, `Wait For Condition`, `Wait For Function`, `Wait For Request`, `Wait For Response`, promises with `Promise To` and `Wait For`, `Http`, `Go To`, `Go Back` and `Go Forward`, and the timeouts and retries of `Set Browser Timeout` and `Set Retry Assertions For`. |
| Context state | Works | Cookies, local and session storage, `Grant Permissions`, `Set Geolocation`, `Set Offline`, `Emulate Media`, `Set Viewport Size` and the clock keywords `Set Time`, `Pause At` and `Advance Clock`. `Get Viewport Size` returns `None` until `Set Viewport Size` emulates a size; the window keeps its own size. `Save Storage State` works only while every http and https origin that the application has visited is open in a window, and it leaves out the storage of `file://` pages. `Set Storage State` is hidden. |
| Dialogs | Works | `alert` and `confirm` with `Handle Future Dialogs`, `Wait For Alert` and `Wait For Alerts`. Without a handler, Playwright dismisses them. Electron has no `prompt()`, see [Behaviour of Electron](#behaviour-of-electron). Both kinds of handler on the same page crash Browser's Node process, and so does a `beforeunload` handler, see [Known crashes](#known-crashes). Native dialogs need the main process. |
| Downloads | Works | `Promise To Wait For Download` after a click, also with `wait_for_finished=False` and `Get Download State`, and `Download` from a page loaded from a URL. `Cancel Download` cancels a running download. The libraries tell Browser that the application accepts downloads, as Electron does. |
| Pages and windows | Works | Windows that the application opens later: `Switch Window` with their title. `<webview>`s and `WebContentsView`s are pages too, but select them by page id, see [Pages and windows](#pages-and-windows). A window that the application closes leaves `Get Page Ids`. `Close Page` closes windows and `WebContentsView`s, but waits forever on a `<webview>`. On the last window, it ends most applications, through their `window-all-closed` handler. |
| Screenshots, recordings and coverage | Works | `Take Screenshot` of the window or an element; screenshots have the window's size. Videos, traces and HAR files come from `record_video`, `tracing` and `record_har` of `Start Electron Application`, see [Videos and slow motion](../videos/) and [Traces and HAR files](../traces/). `Start Coverage`, `Highlight Elements`, `Add Style Tag` and presenter mode work. Playwright has no `slowMo` for Electron; presenter mode slows a test down instead. |
| Applications | Own keywords | `Switch Electron Application`, `Get Electron Application Ids` and `Get Electron Application Catalog` replace Browser's keywords for browsers and contexts, see [Compared with the Browser library](#compared-with-the-browser-library). |
| Other keywords | Works | From the audit: locator handlers, WebAuthn credentials (`Create Credential` and the related keywords), `Register Keyword To Run On Failure`, `Show Keyword Banner` and `Set Strict Mode`. |

## Compared with the Browser library

`Electron` and `VSCode` hide the Browser keywords for browsers and contexts, because an application is one browser with one context, and the keywords that cannot work on an application. They offer these keywords instead:

| Browser keyword | In `Electron` and `VSCode` | Why |
|---|---|---|
| `New Browser`, `New Persistent Context`, `Open Browser` | `Start Electron Application`, `Start VS Code` | A test starts an application. |
| `Close Browser`, `Close Context` | `Close Electron Application`, `Close VS Code` | The application ends with its only context. |
| `Switch Browser` | `Switch Electron Application` | Several applications can be open at once. |
| `Get Browser Ids` | `Get Electron Application Ids` | It returns the ids of the open applications. |
| `Get Browser Catalog` | `Get Electron Application Catalog` | It leaves out the context level. |
| `New Context`, `Switch Context`, `Get Context Ids` | – | An application has exactly one context. |
| `New Page` | – | The application opens its windows itself. |
| `Launch Browser Server`, `Close Browser Server`, `Connect To Browser` | – | For browsers only. |
| `Get Device`, `Get Devices` | – | Devices are options for `New Context`. |
| `Crawl Site` | – | It opens pages of its own. |
| `Set Storage State` | – | It needs a page of its own to write the storage. |
| `Tap` | – | Touch input is not enabled for applications. |
| `Save Page As Pdf` | – | Electron, and with it VS Code, does not provide Chromium's PDF printing over the DevTools protocol. |

A test that needs a web browser as well imports the Browser library beside `Electron` or `VSCode`. Keywords that both libraries have then need the library name:

```robotframework
*** Settings ***
Library    Electron
Library    Browser

*** Test Cases ***
Web Page Beside An Application
    Start Electron Application    /opt/my-app/my-app
    Browser.New Browser    chromium    headless=True
    Browser.New Page    https://example.com/
    Electron.Get Title    ==    My App
```

## Keywords that fail

These visible keywords fail on an application under some conditions. The acceptance tests expect the error, so an upgrade that lifts the limitation is noticed.

| Keyword | Error | Cause |
|---|---|---|
| `Save Storage State` | `Protocol error (Target.createTarget): Not supported` | Only when an http or https origin that the application has visited is no longer open in a window: reading its storage then needs a page of its own, which an application cannot open. |

## Locators

Selectors behave as in a web browser. Some details:

- **Shadow roots:** CSS, `id=` and `text=` find elements in open shadow roots. `css:light=`, `id:light=`, `text:light=` and XPath do not.
- **Iframes:** `>>>` reaches into iframes, for example `id=frame >>> id=in-frame`.
- **`aria-ref=`:** it finds elements by the references in `Get Aria Snapshot    <selector>    mode=ai`, such as `aria-ref=e5`. The references change with every snapshot, so they help to explore an application, not to write tests.
- **`_react=` and `_vue=`:** Playwright 1.63 still accepts them, but they fail with "Cannot read properties of undefined (reading 'queryAll')".
- **Your own selector engine:** a [JavaScript extension](https://robotframework-browser.org/docs/extending/javascript-extensions/) can register one with Playwright's `selectors.register`. It applies to pages that load after the registration, so register it before the application starts, or `Reload` the windows that are already open.

```js
async function registerTagEngine(playwright) {
    await playwright.selectors.register('tag', () => ({
        query: (root, selector) => root.querySelector(selector),
        queryAll: (root, selector) => Array.from(root.querySelectorAll(selector)),
    }));
}

exports.__esModule = true;
exports.registerTagEngine = registerTagEngine;
```

```robotframework
*** Settings ***
Library    Electron    jsextension=${CURDIR}/selector_engine.js

*** Test Cases ***
Find By Tag Name
    Register Tag Engine
    Start Electron Application    /opt/my-app/my-app
    Get Text    tag=h1    ==    My App
```

## Pages and windows

Every window of the application is a page, and so is every `<webview>` and every `WebContentsView`. The window keywords know which pages are windows: `Get Window Ids` and `Get Window Titles` list only the windows, and `Switch Window` switches only to them. They take a window by the title that it shows, `title=Settings`, by a regular expression for that title in the form of Browser's `text=` selector, `title=/^Settings/i`, or by its id from `Get Window Ids`, which is valid while the application runs and unique only within it.

Switch to a window that the application opens by its title. `Switch Window` waits until a window shows it:

```robotframework
Click    text=Settings
${previous} =    Switch Window    title=Settings
Click    text=Save
Switch Window    ${previous}
```

`Switch Window    NEW` and `Switch Page    NEW` take the newest page if it is newer than the active page. That can be a `<webview>` or `WebContentsView` that loaded after the new window, which `Switch Window` refuses, or, after a switch back to an older window, a page that was open before. A title has neither problem. `Switch Window` finds the page of a window through the title of that page, so a window whose page has no title, or shares its title with another page, is switched to with its page id.

`<webview>`s and `WebContentsView`s are selected with `Switch Page` and their page id, which `Get Electron Application Catalog` lists with their titles. A keyword that switches to the page with a given title:

```robotframework
*** Keywords ***
Switch To Page With Title
    [Arguments]    ${title}
    ${catalog} =    Get Electron Application Catalog
    FOR    ${application}    IN    @{catalog}
        FOR    ${page}    IN    @{application}[pages]
            IF    $application["active"] and $page["title"] == $title
                Switch Page    ${page}[id]
                RETURN
            END
        END
    END
    Fail    No page with the title '${title}'.
```

- **`>>>` and `<webview>`:** a `<webview>` is not an iframe, so `>>>` does not reach into it; it fails with "<iframe> was expected". Switch to the `<webview>`'s page instead.
- **Closing a `<webview>`:** `Close Page` waits forever on a `<webview>`'s page, because the `<webview>` element in its host page keeps it. Remove the element instead; its page then goes away:

  ```robotframework
  Evaluate JavaScript    id=guest    (element) => element.remove()
  ```

  `Close Page` on a `WebContentsView`'s page closes it and removes the view from its window.
- **An application that quits by itself** stays in Browser's catalog with an empty context. Keywords then fail with "No page open." until `Close Electron Application`, which also passes for an application that has already quit.

## Behaviour of Electron

- **Color scheme:** by default, the application decides its color scheme. `color_scheme` of `Start Electron Application` sets one, see [launch options](../getting-started/#launch-options).
- **Window size:** a window has the size that the application gives it; there is no emulated viewport, so `Get Viewport Size` returns `None`. `Set Window Size` sizes the window and `Get Window Size` returns its size, which its page, its screenshots and its video have. `Set Viewport Size` emulates a viewport inside the page.
- **Maximising and minimising:** `Maximize Window`, `Minimize Window` and `Restore Window` need a window manager, such as Openbox, which the display profiles start, see [CI and the Linux display](../../running/ci-and-display/#display-profiles). On plain Xvfb without one, maximising and minimising fail after the timeout, while `Set Window Size` works. Some Wayland desktops, such as niri, cannot minimise windows.
- **Minimised windows** draw nothing, so Browser keywords on their pages wait until their timeout. Call `Restore Window` before acting on such a window again.
- **Locale and time zone:** they follow the system. `locale` and `timezone_id` set them for the windows; `--lang` in `args` and `TZ` in `env` set them for the main process.
- **User data:** Electron keeps cookies, local storage and other data of an application in its user-data folder, on Linux `~/.config/<name>`, on Windows `%APPDATA%\<name>` and on macOS `~/Library/Application Support/<name>`, so they last from one run to the next. `args=--user-data-dir=<folder>` with a new, empty folder starts the application without them, unless it sets the folder itself with `app.setPath`.
- **`prompt()`:** Electron does not implement it. A page's call fails with "prompt() is not supported.", so `prompt_input` of `Handle Future Dialogs` never applies.
- **Native dialogs:** file dialogs and message boxes are not part of a page. Replace them in the main process, see [the main process](../getting-started/#the-main-process).

### Shortcuts and menus

Keyboard keywords send keys to the page. The accelerators of the application's menu and `before-input-event` handlers in the main process do not see them, so a shortcut that only the menu handles does nothing. Click the menu item in the main process instead. `getMenuItemById` finds items that have an `id` in the application's menu template:

```robotframework
Evaluate In Main Process    ({ Menu }) => Menu.getApplicationMenu().getMenuItemById('open-file').click()
```

## Known crashes

Two problems end Browser's Node process, and with it every later test of the run. They come from Playwright and Browser, not from these libraries.

- **A `beforeunload` handler.** In Electron, a `beforeunload` handler that returns a value cancels leaving or closing the page without asking; Electron recommends this to keep a window open. Playwright still sees a dialog, fails to dismiss it, and Browser's Node process exits. `Go To` to another page, `Close Page    runBeforeUnload=True`, `Close Electron Application` and Browser's automatic closing are affected. Remove the handler before such a step:

  ```robotframework
  Evaluate JavaScript    ${None}    () => { window.onbeforeunload = null; }
  Close Electron Application
  ```

  A handler added with `addEventListener` cannot be removed like this. The application then needs a way to switch it off for tests.
- **`Handle Future Dialogs` and `Wait For Alert` on the same page.** Both accept the same dialog, the second one fails, and the Node process exits. This happens in a web browser too, but an application's window stays the same page across tests, so a handler from an earlier test is still active. Use one of the two per page, or start the application in each test.
