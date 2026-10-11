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
        const window = await app.firstWindow({ timeout });
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

// Runs the function text `script` in the main process of the application with
// the browser id `browserId`, with the electron module, `arg`, and the
// BrowserWindow of the active `page` if the page belongs to the application.
async function robotframeworkElectronEvaluate(browserId, script, arg, page) {
    const application = applications.get(browserId);
    if (!application) {
        throw new Error(`Browser '${browserId}' is not an application started by 'New Electron Application'.`);
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
