const { contextBridge, ipcRenderer } = require('electron');

// Expose APIs in the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Function to select a folder
    selectFolder: () => ipcRenderer.invoke('select-folder'),

    // Function to organize files from the source folder to the destination folder
    // Now it includes the size parameters
    organizeFiles: (srcFolder, destFolder, sizeConfig) => ipcRenderer.invoke('organize-files', srcFolder, destFolder, sizeConfig)
});
