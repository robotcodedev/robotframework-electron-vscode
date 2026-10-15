// Minimal Electron app for the acceptance tests of the Electron library.
// Start with `--no-window` to get an app that never opens a window,
// `--dark` to switch its theme to dark, `--page=<file>` to load another page,
// and `--views` to load views.html, which has a <webview>, and to add a WebContentsView.
const { app, BrowserWindow, Menu, WebContentsView, dialog, ipcMain, nativeTheme } = require('electron');
const path = require('node:path');

// The tests run under Xvfb without a GPU. A GPU process that hangs while it starts stops the window's frames
// until Chromium's watchdog falls back to software rendering, so the app renders in software from the start.
app.disableHardwareAcceleration();

const views = process.argv.includes('--views');
const pageArgument = process.argv.find((arg) => arg.startsWith('--page='));
const page = pageArgument ? pageArgument.slice('--page='.length) : views ? 'views.html' : 'index.html';

// Calls dialog.showOpenDialog through the module, so that a test can replace it.
ipcMain.handle('open-file', async () => {
    const result = await dialog.showOpenDialog({ properties: ['openFile'] });
    return result.canceled ? '' : result.filePaths[0];
});

let mainWindow;

// A menu item with an accelerator. When clicked, it marks the main window's page with data-menu.
Menu.setApplicationMenu(
    Menu.buildFromTemplate([
        { role: 'editMenu' },
        {
            label: 'Fixture',
            submenu: [
                {
                    id: 'greet',
                    label: 'Greet',
                    accelerator: 'CmdOrCtrl+Shift+G',
                    click: () => mainWindow?.webContents.executeJavaScript("document.body.dataset.menu = 'greet'"),
                },
            ],
        },
    ]),
);

app.whenReady().then(() => {
    if (process.argv.includes('--no-window')) return;
    if (process.argv.includes('--dark')) nativeTheme.themeSource = 'dark';
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: { preload: path.join(__dirname, 'preload.js'), webviewTag: views },
    });
    mainWindow.loadFile(path.join(__dirname, page), {
        query: {
            args: JSON.stringify(process.argv.slice(2)),
            cwd: process.cwd(),
            testVar: process.env.ROBOT_TEST_VAR || '',
            runOnlyVar: process.env.ROBOT_ONLY_IN_RUN || '',
            runAsNode: process.env.ELECTRON_RUN_AS_NODE || '',
        },
    });
    if (views) {
        const view = new WebContentsView();
        mainWindow.contentView.addChildView(view);
        view.setBounds({ x: 0, y: 400, width: 400, height: 150 });
        view.webContents.loadFile(path.join(__dirname, 'view.html'));
    }
});

app.on('window-all-closed', () => app.quit());
