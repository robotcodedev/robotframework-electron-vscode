// Loaded into the Browser library's Node process by the Electron library.
// The function name is prefixed because Browser resolves extension functions
// by name across all loaded modules.

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, recordVideo, playwright, adoptContext) {
    const app = await playwright._electron.launch({
        executablePath,
        args,
        env,
        cwd: cwd || undefined,
        timeout,
        recordVideo: recordVideo || undefined,
    });
    let window;
    try {
        window = await app.firstWindow({ timeout });
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
    const adopted = await adoptContext(app.context());
    return { ...adopted, videoPath: recordVideo ? await window.video()?.path() : null };
}

exports.__esModule = true;
exports.robotframeworkElectronLaunch = robotframeworkElectronLaunch;
