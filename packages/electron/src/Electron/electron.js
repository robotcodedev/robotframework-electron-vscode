// Loaded into the Browser library's Node process by the Electron library.
// The function name is prefixed because Browser resolves extension functions
// by name across all loaded modules.

async function robotframeworkElectronLaunch(executablePath, args, env, cwd, timeout, playwright, adoptContext) {
    const app = await playwright._electron.launch({
        executablePath,
        args,
        env,
        cwd: cwd || undefined,
        timeout,
    });
    try {
        await app.firstWindow({ timeout });
    } catch (error) {
        await app.close().catch(() => app.process().kill());
        throw error;
    }
    return adoptContext(app.context());
}

exports.__esModule = true;
exports.robotframeworkElectronLaunch = robotframeworkElectronLaunch;
