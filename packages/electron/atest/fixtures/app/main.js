// Minimal Electron app for the acceptance tests of the Electron library.
// Start with `--no-window` to get an app that never opens a window,
// `--dark` to switch its theme to dark, and `--page=<file>` to load another page.
const { app, BrowserWindow, nativeTheme } = require('electron');
const path = require('node:path');

const pageArgument = process.argv.find((arg) => arg.startsWith('--page='));
const page = pageArgument ? pageArgument.slice('--page='.length) : 'index.html';

app.whenReady().then(() => {
    if (process.argv.includes('--no-window')) return;
    if (process.argv.includes('--dark')) nativeTheme.themeSource = 'dark';
    const win = new BrowserWindow({ width: 800, height: 600 });
    win.loadFile(path.join(__dirname, page), {
        query: {
            args: JSON.stringify(process.argv.slice(2)),
            cwd: process.cwd(),
            testVar: process.env.ROBOT_TEST_VAR || '',
            runOnlyVar: process.env.ROBOT_ONLY_IN_RUN || '',
            runAsNode: process.env.ELECTRON_RUN_AS_NODE || '',
        },
    });
});

app.on('window-all-closed', () => app.quit());
