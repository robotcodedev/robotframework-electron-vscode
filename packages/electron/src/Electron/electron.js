// Loaded into the Browser library's Node process by the Electron library.
// The function name is prefixed because Browser resolves extension functions
// by name across all loaded modules.

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, recordVideo, recordHar, tracing, playwright, adoptContext) {
    // Browser releases without the hook pass a placeholder instead of a function.
    if (typeof adoptContext !== 'function') {
        throw new Error('The Browser library has no adoptContext hook, which the Electron library needs to take over the application.');
    }
    // The options of the application's browser context, as Playwright gets them.
    // Browser keeps them with the context, so that keywords such as Download work.
    const contextOptions = { acceptDownloads: true };
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
        const adopted = await adoptContext(app.context(), { name: 'electron', tracing: tracing || undefined, contextOptions });
        return { ...adopted, videoPath: recordVideo ? await window.video()?.path() : null };
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
}

exports.__esModule = true;
exports.robotframeworkElectronLaunch = robotframeworkElectronLaunch;
