function GetCallingFuncName() 
{
   var funName = arguments.caller.toString();
   funName = funName.substr('function '.length);
   funName = funName.substr(0, funName.indexOf('('));

   return funName;
}

function CentemeterToFoot(centemeters)
{
    return centemeters / 30.48;
}

function FootToCentemeter(feet)
{
    return feet * 30.48;
}

function c_Land()
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Emergency()
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Up(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.z += CentemeterToFoot(parseFloat(args[0]));
}

function c_Down(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.z -= CentemeterToFoot(parseFloat(args[0]));

    if(COPTER_DEST.z < 0) { COPTER_DEST.z = 0; }
}

function c_Left(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.x -= CentemeterToFoot(parseFloat(args[0]));
}

function c_Right(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.x += CentemeterToFoot(parseFloat(args[0]));
}

function c_Forward(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.y -= CentemeterToFoot(parseFloat(args[0]));
}

function c_Back(args)
{ 
    console.log("Executing: " + arguments.callee.name) 
    COPTER_DEST.y += CentemeterToFoot(parseFloat(args[0]));

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