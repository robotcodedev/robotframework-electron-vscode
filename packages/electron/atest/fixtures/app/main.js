// Minimal Electron app for the acceptance tests of the Electron library.
// Start with `--no-window` to get an app that never opens a window.
const { app, BrowserWindow } = require('electron');
const path = require('node:path');

app.whenReady().then(() => {
    if (process.argv.includes('--no-window')) return;
    const win = new BrowserWindow({ width: 800, height: 600 });
    win.loadFile(path.join(__dirname, 'index.html'), {
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
