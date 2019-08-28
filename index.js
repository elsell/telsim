const { app, BrowserWindow, ipcMain } = require('electron');
const WebSocket              = require('ws');
const WEB_SOCKET_PORT        = 9990;
const COMMAND_KEY            = "quad-command";

const wss = new WebSocket.Server({port: WEB_SOCKET_PORT});
let window;

let DEBUG = true;

// Recieve Message on WebSocket from Client
wss.on('connection', ws => {
    ws.on('message', message => {
        Log(`Received: ${message}`);

        // Send recieved message to the renderer window
        window.webContents.send(COMMAND_KEY, String(message));
    }) 
});

// Recieve Response from Renderer to Send to Client
ipcMain.on('synchronous-message', (event, arg) => {
    Log("Responding: " + String(arg));
    event.returnValue = 'recieved';

    wss.clients.forEach(function each(client) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(arg);
    }});
  });
  
function CreateWindow ()
{
    // Create Browser Window
    window = new BrowserWindow({
        width:  800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });

    // and load renderer webpage
    window.loadFile("renderer/index.html");

    window.webContents.on('crashed', (e) => {
        Log(e);
        app.quit()
    });
}

function Log(message)
{
    if(DEBUG)
    {
        console.log("[LOG]", message);
    }
}

app.on('ready', CreateWindow);

app.on('quit', () => {
    Log("Cleaning Up...");
    wss.close();
    app.quit()
});