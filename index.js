const { app, BrowserWindow } = require('electron');
const WebSocket              = require('ws');
const WEB_SOCKET_PORT        = 9990;
const COMMAND_KEY            = "quad-command";

const wss = new WebSocket.Server({port: WEB_SOCKET_PORT});
let window;

let DEBUG = true;

wss.on('connection', ws => {
    ws.on('message', message => {
        Log("Recieved: ", message);

        // Send recieved message to the renderer window
        window.webContents.send(COMMAND_KEY, message);
    })
})

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
}

function Log(message)
{
    if(DEBUG)
    {
        print("[LOG] ", message);
    }
}

app.on('ready', CreateWindow);
