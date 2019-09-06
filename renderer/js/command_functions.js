function GetCallingFuncName() 
{
   var funName = arguments.caller.toString();
   funName = funName.substr('function '.length);
   funName = funName.substr(0, funName.indexOf('('));

   return funName;
}

// Returns true if (lowerBound <= val <= upperBound)
function IsInRange(val, lowerBound, upperBound)
{
    return(val >= lowerBound && val <= upperBound);
}

function CentemeterToFoot(centemeters)
{
    return centemeters / 30.48;
}

function FootToCentemeter(feet)
{
    return feet * 30.48;
}

function c_Land(callingCmd)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Emergency(callingCmd)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Up(args)
{ 
    console.log("Executing: " + arguments.callee.name) 

    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'up' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.z += CentemeterToFoot(dist);
    SendResponseCode(true);
}

function c_Down(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'down' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.z -= CentemeterToFoot(dist);

    if(COPTER_DEST.z < 0) { COPTER_DEST.z = 0; }
    SendResponseCode(true);
    
}

function c_Left(args)
{ 
    console.log("Executing: " + arguments.callee.name);
    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'left' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.x -= CentemeterToFoot(dist);
    SendResponseCode(true);
}

function c_Right(args)
{ 
    console.log("Executing: " + arguments.callee.name);
    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'right' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.x += CentemeterToFoot(dist);
    SendResponseCode(true);
}

function c_Forward(args)
{ 
    console.log("Executing: " + arguments.callee.name);
    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'forward' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.y -= CentemeterToFoot(dist);
    SendResponseCode(true);
}

function c_Back(args)
{ 
    console.log("Executing: " + arguments.callee.name);
    var dist = parseFloat(args[0]);

    if(!IsInRange(dist, 20, 500))
    {
        SendResponseCode(false, "Distance parameter for 'back' must be between"
         + " 20 and 500.");
         return;
    }

    COPTER_DEST.y += CentemeterToFoot(dist);
    SendResponseCode(true);
}

function c_Cw(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Ccw(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Flip(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Go(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Stop()
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Curve(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Speed(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}