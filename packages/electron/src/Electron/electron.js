// Loaded into the Browser library's Node process by the Electron library.
// The function names are prefixed because Browser resolves extension functions
// by name across all loaded modules.

// The started applications by browser id, until Browser closes them.
const applications = new Map();

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, recordVideo, recordHar, tracing, launchOptions, defaultTimeout, playwright, adoptContext) {
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
        ...contextOptions,
    });
    try {
        const window = await firstWindowPage(app, await app.firstWindow({ timeout }), timeout);
        // The library timeout, as the contexts that Browser creates get it.
        app.context().setDefaultTimeout(defaultTimeout);
        let browserId;
        const onClose = async () => {
            applications.delete(browserId);
        };
        const adopted = await adoptContext(app.context(), { name: 'electron', tracing: tracing || undefined, contextOptions, onClose });
        browserId = adopted.browserId;
        applications.set(browserId, app);
        return { ...adopted, videoPath: recordVideo ? await window.video()?.path() : null };
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
}

// Whether `page` shows the own contents of a BrowserWindow, and not a WebContentsView
// or a <webview> inside one. A page that has closed is none.
async function isWindowPage(app, page) {
    if (page.isClosed()) return false;
    try {
        const session = await page.context().newCDPSession(page);
        const { targetInfo } = await session.send('Target.getTargetInfo');
        await session.detach();
        return await app.evaluate(({ BrowserWindow, webContents }, targetId) => {
            const contents = webContents.fromDevToolsTargetId(targetId);
            return contents !== undefined && BrowserWindow.fromWebContents(contents)?.webContents === contents;
        }, targetInfo.targetId);
    } catch (error) {
        if (page.isClosed()) return false;
        throw error;
    }
}

// The page of the application's first window. Views and <webview>s are pages too, and
// Playwright may see one of them first; then this waits for the window's own page.
async function firstWindowPage(app, first, timeout) {
    if (first.isClosed() || (await isWindowPage(app, first))) return first;
    const deadline = Date.now() + timeout;
    for (;;) {
        for (const page of app.windows()) {
            if (await isWindowPage(app, page)) return page;
        }
        if (timeout && Date.now() > deadline) {
            throw new Error(`The application showed no window of its own within ${timeout} ms, only views.`);
        }
        await new Promise((resolve) => setTimeout(resolve, 100));
    }
}

// Whether the active `page` is a window's own page of the application with the browser id `browserId`.
async function robotframeworkElectronIsWindowPage(browserId, page) {
    const application = applications.get(browserId);
    if (!application || !page || page.context() !== application.context()) return false;
    return isWindowPage(application, page);
}

// Runs the function text `script` in the main process of the application with
// the browser id `browserId`, with the electron module, `arg`, and the
// BrowserWindow of the active `page` if the page belongs to the application.
async function robotframeworkElectronEvaluate(browserId, script, arg, page) {
    const application = applications.get(browserId);
    if (!application) {
        throw new Error(`Browser '${browserId}' is not an application started by 'Start Electron Application'.`);
    }
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
exports.robotframeworkElectronIsWindowPage = robotframeworkElectronIsWindowPage;
