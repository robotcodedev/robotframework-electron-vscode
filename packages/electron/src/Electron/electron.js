// Loaded into the Browser library's Node process by the Electron library.
// The function name is prefixed because Browser resolves extension functions
// by name across all loaded modules.

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, recordVideo, recordHar, tracing, playwright, adoptContext) {
    // The options of the application's browser context, as Playwright gets them.
    // Browser keeps them with the context, so that keywords such as Download work.
    const contextOptions = { acceptDownloads: true };
    if (recordVideo) contextOptions.recordVideo = recordVideo;
    if (recordHar) contextOptions.recordHar = recordHar;
    const app = await playwright._electron.launch({
        executablePath,
        args,
        env,
        cwd: cwd || undefined,
        timeout,
        ...contextOptions,
    });
    let window;
    try {
        window = await app.firstWindow({ timeout });
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
    const adopted = await adoptContext(app.context(), { name: 'electron', tracing: tracing || undefined, contextOptions });
    return { ...adopted, videoPath: recordVideo ? await window.video()?.path() : null };
}

exports.__esModule = true;
exports.robotframeworkElectronLaunch = robotframeworkElectronLaunch;
