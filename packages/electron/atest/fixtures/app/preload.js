// Gives the fixture's pages a way to open a native file dialog in the main process.
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('fixture', {
    openFile: () => ipcRenderer.invoke('open-file'),
});
