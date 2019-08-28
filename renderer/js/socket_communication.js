var ipcRenderer   = require('electron').ipcRenderer;
const COMMAND_KEY = "quad-command";

// Recieve Command
ipcRenderer.on(COMMAND_KEY, (e, command) =>
{
    console.log(command);
});

function SendResponseCode(ok = true, errorCode = "")
{
    if(ok)
    {
        RespondToClient("ok");
    }
    else
    {
        if(errorCode !== "")
        {
            RespondToClient(errorCode);
        }
        else
        {
            RespondToClient("error");
        }
    }
}

function RespondToClient(message)
{
    ipcRenderer.send('synchronous-message', message);
}