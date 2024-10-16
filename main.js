const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const axios = require("axios");
const { spawn } = require("child_process"); // Import child_process to run the Python script

function createWindow() {
  const win = new BrowserWindow({
    width: 450,
    height: 450,
    maxHeight: 450,
    maxWidth: 450,
    minHeight: 450,
    minWidth: 450,
    resizable: false,
    title: "File Organizer",
    fullscreenable: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"), // Reference preload script
      nodeIntegration: false, // Ensure security best practices
      contextIsolation: true, // Isolate context for security
    },
  });

  win.loadFile("index.html");
}

// Function to run the Python script
function runPythonScript() {
  const pythonProcess = spawn("python3", [path.join(__dirname, "file_organizer.py")]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Python Output: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  runPythonScript(); // Run the Python script when the app is ready
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// Handle folder selection via dialog
ipcMain.handle("select-folder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"], // Ensure only directories can be selected
  });
  return result.canceled ? null : result.filePaths[0]; // Return folder path if selected, otherwise null
});

// Handle file organization request, now with size-based functionality
ipcMain.handle("organize-files", async (event, srcFolder, destFolder, sizeConfig) => {
  try {
    // Make POST request to Flask API, now passing size configuration
    const response = await axios.post("http://127.0.0.1:5000/organize", {
      srcFolder: srcFolder,
      destFolder: destFolder,
      sizeConfig: sizeConfig, // Include sizeConfig in the request body
    });
    return response.data; // Return success or error message from Flask
  } catch (error) {
    return { status: "error", message: error.message }; // Handle any errors during request
  }
});

