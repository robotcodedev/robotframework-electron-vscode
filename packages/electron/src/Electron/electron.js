// Loaded into the Browser library's Node process by the Electron library.
// The function names are prefixed because Browser resolves extension functions
// by name across all loaded modules.

// The started applications by browser id, until Browser closes them.
const applications = new Map();

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, recordVideo, recordHar, tracing, tracesDir, launchOptions, playwright, adoptContext) {
    // Browser releases without the hook pass a placeholder instead of a function.
    if (typeof adoptContext !== 'function') {
        throw new Error('The Browser library has no adoptContext hook, which the Electron library needs to take over the application.');
    }
    // The options of the application's browser context, as Playwright gets them.
    // Browser keeps them with the context, so that keywords such as Download work.
    // Without colorScheme, Playwright would emulate a light one; null leaves it to the application.
    const contextOptions = { acceptDownloads: true, colorScheme: null, ...launchOptions };
    if (recordVideo) contextOptions.recordVideo = recordVideo;
    if (recordHar) contextOptions.recordHar = recordHar;
    const app = await playwright._electron.launch({
        executablePath,
        args,
        env,
        cwd,
        timeout,
        tracesDir,
        ...contextOptions,
    });
    try {
        const window = await firstWindowPage(app, await app.firstWindow({ timeout }), timeout);
        let browserId;
        const onClose = async () => {
            applications.delete(browserId);
        };
        // A window that closed during the start is no page of the context any more.
        const activePage = window.isClosed() ? undefined : window;
        const adopted = await adoptContext(app.context(), {
            name: 'electron',
            tracing: tracing || undefined,
            contextOptions,
            onClose,
            activePage,
        });
        browserId = adopted.browserId;
        applications.set(browserId, app);
        return adopted;
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
}

// The id of the BrowserWindow whose own contents `page` shows, or null for a WebContentsView
// or a <webview> inside one, and for a page that has closed.
async function windowIdOfPage(app, page) {
    if (page.isClosed()) return null;
    try {
        const session = await page.context().newCDPSession(page);
        const { targetInfo } = await session.send('Target.getTargetInfo');
        await session.detach();
        return await app.evaluate(({ BrowserWindow, webContents }, targetId) => {
            const contents = webContents.fromDevToolsTargetId(targetId);
            const window = contents && BrowserWindow.fromWebContents(contents);
            return window && window.webContents === contents ? window.id : null;
        }, targetInfo.targetId);
    } catch (error) {
        if (page.isClosed()) return null;
        throw error;
    }
}

// The page of the application's first window. Views and <webview>s are pages too, and
// Playwright may see one of them first; then this waits for the window's own page.
async function firstWindowPage(app, first, timeout) {
    if (first.isClosed() || (await windowIdOfPage(app, first)) !== null) return first;
    const deadline = Date.now() + timeout;
    for (;;) {
        for (const page of app.windows()) {
            if ((await windowIdOfPage(app, page)) !== null) return page;
        }
        if (timeout && Date.now() > deadline) {
            throw new Error(`The application showed no window of its own within ${timeout} ms, only views.`);
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
}

// The application that `Start Electron Application` started as the browser `browserId`.
function startedApplication(browserId) {
    const application = applications.get(browserId);
    if (!application) {
        throw new Error(`Browser '${browserId}' is not an application started by 'Start Electron Application'.`);
    }
    return application;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// The id of the window that `window` names: `window=<n>` or `<n>`, an id from `Get Window Ids`, or
// `title=<title>`, the title that exactly one window shows, or `title=/<pattern>/<flags>`, a regular
// expression that exactly one window's title matches, waited for up to `timeout` ms. Without
// `window`, the window that shows the active `page`, which for a view or <webview> is the window around it.
async function findWindow(app, window, page, timeout) {
    if (!window) {
        if (!page || page.context() !== app.context()) {
            throw new Error('The active page is no page of the application.');
        }
        const handle = await app.browserWindow(page);
        try {
            const id = await handle.evaluate((browserWindow) => browserWindow?.id ?? null);
            if (id === null) throw new Error('The active page is in no window of the application.');
            return id;
        } finally {
            await handle.dispose();
        }
    }
    const number = /^(?:window=)?(\d+)$/.exec(window)?.[1];
    if (number !== undefined) {
        const id = Number(number);
        if (await app.evaluate(({ BrowserWindow }, id) => BrowserWindow.fromId(id) === null, id)) {
            throw new Error(`The application has no window 'window=${id}'.`);
        }
        return id;
    }
    if (!window.startsWith('title=')) {
        throw new Error(`'${window}' names no window. Give a window as 'title=<title>' or as an id from 'Get Window Ids'.`);
    }
    const title = window.slice('title='.length);
    // As in Browser's text selector, a title between slashes, followed by flags, is a regular expression.
    const expression = /^\/(.*)\/([dgimsuvy]*)$/s.exec(title);
    if (expression) {
        try {
            new RegExp(expression[1], expression[2]);
        } catch (error) {
            throw new Error(`'${window}' is no valid regular expression: ${error.message}`);
        }
    }
    const match = expression ? { source: expression[1], flags: expression[2] } : { title };
    const described = expression ? `a title that matches ${title}` : `the title '${title}'`;
    const deadline = Date.now() + timeout;
    for (;;) {
        const ids = await app.evaluate(({ BrowserWindow }, match) => {
            // A new expression for each title, because one with the flags g or y remembers where it stopped.
            const matches = (title) =>
                match.title !== undefined ? title === match.title : new RegExp(match.source, match.flags).test(title);
            return BrowserWindow.getAllWindows()
                .filter((browserWindow) => matches(browserWindow.getTitle()))
                .map((browserWindow) => browserWindow.id)
                .sort((a, b) => a - b);
        }, match);
        if (ids.length === 1) return ids[0];
        if (Date.now() >= deadline) {
            if (ids.length === 0) throw new Error(`No window shows ${described}.`);
            const names = ids.map((id) => `window=${id}`).join(', ');
            throw new Error(`${ids.length} windows show ${described}: ${names}.`);
        }
        await sleep(100);
    }
}

// Runs in the main process. Brings the window `id` into `state`, maximized, minimized or normal, and
// then to the content size `size`, if it is given, and polls every 50 ms until the window is there or
// `timeout` ms are over. Returns the window's state and content size, and whether it got there.
async function adjustWindow({ BrowserWindow, screen }, { id, state, size, timeout }) {
    const window = BrowserWindow.fromId(id);
    if (!window) throw new Error(`The application has no window 'window=${id}'.`);
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const deadline = Date.now() + timeout;
    const stateOf = () => {
        if (window.isFullScreen()) return 'fullscreen';
        return window.isMinimized() ? 'minimized' : window.isMaximized() ? 'maximized' : 'normal';
    };
    const steps = {
        maximized: () => window.maximize(),
        minimized: () => window.minimize(),
        // A minimised window comes back in its previous state, which may be maximised.
        normal: () => (window.isMinimized() ? window.restore() : window.unmaximize()),
    };
    // A state counts once two polls in a row see it: on its way, a window can pass through another
    // state, for example normal when a minimised window comes back maximised. A request is made once
    // per state that the window is in, so a window manager that ignores it is not asked again and again.
    let asked = null;
    let seen = 0;
    while (Date.now() < deadline) {
        const current = stateOf();
        if (current !== state) {
            seen = 0;
            if (asked !== current) {
                asked = current;
                // Every change leaves fullscreen first.
                if (current === 'fullscreen') window.setFullScreen(false);
                else steps[state]();
            }
        } else if (asked === null || ++seen === 2) {
            break;
        }
        await sleep(50);
    }
    const fits = () => {
        if (!size) return true;
        // At a fractional display scale, the window's edges snap to whole device pixels.
        const tolerance = Number.isInteger(screen.getDisplayMatching(window.getBounds()).scaleFactor) ? 0 : 2;
        const [width, height] = window.getContentSize();
        return Math.abs(width - size.width) <= tolerance && Math.abs(height - size.height) <= tolerance;
    };
    // The window manager can apply other bounds afterwards, such as those from before the window was
    // maximised, so the size is asked for again while it differs.
    while (stateOf() === state && !fits() && Date.now() < deadline) {
        window.setContentSize(size.width, size.height);
        await sleep(50);
    }
    const [width, height] = window.getContentSize();
    return { state: stateOf(), width, height, reached: stateOf() === state && fits() };
}

// Runs in the main process: the state, maximized, minimized or normal, and the content size of the
// window `id`. A fullscreen window, which fills the screen, counts as maximized.
function readWindow({ BrowserWindow }, id) {
    const window = BrowserWindow.fromId(id);
    if (!window) throw new Error(`The application has no window 'window=${id}'.`);
    const [width, height] = window.getContentSize();
    const maximized = window.isMaximized() || window.isFullScreen();
    return { state: window.isMinimized() ? 'minimized' : maximized ? 'maximized' : 'normal', width, height };
}

// Why the window `id` did not get to `state` and `size` within `timeout` ms. Only the likely
// causes can be named, because the window manager does not report why it ignores a request.
function adjustError(id, state, size, result, timeout) {
    if (result.state !== state) {
        return (
            `The window 'window=${id}' is ${result.state}, not ${state}, after ${timeout} ms. ` +
            'The window manager did not apply the change. Likely causes: a display without a window manager, ' +
            'such as plain Xvfb, which neither maximises nor minimises windows, or a desktop that cannot do it, ' +
            'such as niri, which cannot minimise windows.'
        );
    }
    return (
        `The window 'window=${id}' has the content size ${result.width}x${result.height}, not ` +
        `${size.width}x${size.height}, after ${timeout} ms. Likely causes: the screen is smaller, a tiling ` +
        'window manager decides the size, or the window has a minimum or maximum size.'
    );
}

// Brings the window that `window` names in the application `browserId`, see findWindow, into
// `state` and to the content size `size`, see adjustWindow, and fails if it does not get there.
async function robotframeworkElectronAdjustWindow(browserId, window, state, size, page, defaultTimeout) {
    const application = startedApplication(browserId);
    const deadline = Date.now() + defaultTimeout;
    const id = await findWindow(application, window, page, defaultTimeout);
    const timeout = Math.max(deadline - Date.now(), 0);
    const result = await application.evaluate(adjustWindow, { id, state, size, timeout });
    if (!result.reached) throw new Error(adjustError(id, state, size, result, defaultTimeout));
}

// The state and the content size of the window that `window` names in the application `browserId`,
// see findWindow and readWindow.
async function robotframeworkElectronGetWindow(browserId, window, page, defaultTimeout) {
    const application = startedApplication(browserId);
    const id = await findWindow(application, window, page, defaultTimeout);
    return application.evaluate(readWindow, id);
}

// The ids and titles of the windows of the application `browserId` in the order in which they
// opened, or with `active` of the window that shows the active `page`.
async function robotframeworkElectronWindows(browserId, active, page, defaultTimeout) {
    const application = startedApplication(browserId);
    const only = active ? await findWindow(application, null, page, defaultTimeout) : null;
    return application.evaluate(
        ({ BrowserWindow }, only) =>
            BrowserWindow.getAllWindows()
                .filter((browserWindow) => only === null || browserWindow.id === only)
                .sort((a, b) => a.id - b.id)
                .map((browserWindow) => ({ id: browserWindow.id, title: browserWindow.getTitle() })),
        only,
    );
}

// The id of the window whose own page the active `page` of the application `browserId` is, or null
// for a WebContentsView or a <webview>.
async function robotframeworkElectronWindowOfPage(browserId, page) {
    return windowIdOfPage(startedApplication(browserId), page);
}

// The Playwright page that shows the own contents of the window `id`, or null while there is none.
async function ownPageOf(app, id) {
    for (const page of app.windows()) {
        if ((await windowIdOfPage(app, page)) === id) return page;
    }
    return null;
}

// The id of the window that `window` names in the application `browserId`, see findWindow, and the
// title of the window's own page, read with page.title() as Browser's catalog reads it. For a page
// without a title, webContents.getTitle() would report its URL or file name, which the catalog does
// not list. It waits up to `defaultTimeout` ms until the page has a title, because a page has none
// while it loads, and Playwright sees the page of a new window a moment after the window. The title
// is null if the page has none by then.
async function robotframeworkElectronWindowPage(browserId, window, page, defaultTimeout) {
    const application = startedApplication(browserId);
    const deadline = Date.now() + defaultTimeout;
    const id = await findWindow(application, window, page, defaultTimeout);
    let ownPage = null;
    for (;;) {
        if (!ownPage || ownPage.isClosed()) ownPage = await ownPageOf(application, id);
        // As the catalog does, wait 350 ms for a page that is too busy to answer.
        const title = ownPage ? await Promise.race([ownPage.title().catch(() => ''), sleep(350).then(() => '')]) : '';
        if (title || Date.now() >= deadline) return { id, pageTitle: title || null };
        await sleep(100);
    }
}

// Runs the function text `script` in the main process of the application with
// the browser id `browserId`, with the electron module, `arg`, and the
// BrowserWindow of the active `page` if the page belongs to the application.
async function robotframeworkElectronEvaluate(browserId, script, arg, page) {
    const application = startedApplication(browserId);
    const window = page && page.context() === application.context() ? await application.browserWindow(page) : null;
    try {
        // Playwright sends only this wrapper's text to the main process, so the test's
        // function travels as text and the window as a handle in the argument.
        return await application.evaluate(
            (electron, options) => new Function(`return (${options.script})`)()(electron, options.arg, options.window),
            { script, arg, window },
        );
    } finally {
        await window?.dispose();
    }
}

exports.__esModule = true;
exports.robotframeworkElectronLaunch = robotframeworkElectronLaunch;
exports.robotframeworkElectronEvaluate = robotframeworkElectronEvaluate;
exports.robotframeworkElectronWindows = robotframeworkElectronWindows;
exports.robotframeworkElectronAdjustWindow = robotframeworkElectronAdjustWindow;
exports.robotframeworkElectronGetWindow = robotframeworkElectronGetWindow;
exports.robotframeworkElectronWindowPage = robotframeworkElectronWindowPage;
exports.robotframeworkElectronWindowOfPage = robotframeworkElectronWindowOfPage;
