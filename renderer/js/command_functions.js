function GetCallingFuncName() 
{
   var funName = arguments.caller.toString();
   funName = funName.substr('function '.length);
   funName = funName.substr(0, funName.indexOf('('));

   return funName;
}

function c_Land()
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Emergency()
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Up(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Down(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Left(args)
{ console.log("Executing: " + arguments.callee.name) 
    
}

function c_Right(args)
{ console.log("Executing: " + arguments.callee.name) 

}

function c_Forward(args)
{ console.log("Executing: " + arguments.callee.name) 

}

function c_Back(args)
{ console.log("Executing: " + arguments.callee.name) 

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