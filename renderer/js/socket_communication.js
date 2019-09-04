var ipcRenderer   = require('electron').ipcRenderer;
const COMMAND_KEY = "quad-command";
const CONNECT_STATUS_KEY     = "conn-status";

// Recieve Command
ipcRenderer.on(COMMAND_KEY, (e, command) =>
{
    try
    {
        cmdData = TelloTranslate.Translate(command);

        result = cmdData.func(cmdData.argv);

        SendResponseCode(true);

    }catch(e)
    {
        console.error(e);
        SendResponseCode(false, "404")
    }
});

ipcRenderer.on(CONNECT_STATUS_KEY, (e, status) =>
{
    console.log(status);
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