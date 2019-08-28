class TelloTranslate
{
    constructor()
    {}
    
    static commandMap = 
    {
        "land":{  
            "function":c_Land,
            "argc":0,
            "desc":"Auto landing."
            },
            "emergency":{  
            "function":c_Emergency,
            "argc":0,
            "desc":"Stop motors immediately."
            },
            "up":{  
            "function":c_Up,
            "argc":1,
            "desc":"Ascend to 'x' cm. x = [20,500]"
            },
            "down":{  
            "function":c_Down,
            "argc":1,
            "desc":"Descend to 'x' cm. x = [20,500]"
            },
            "left":{  
            "function":c_Left,
            "argc":1,
            "desc":"Fly left for 'x' cm. x = [20,500]"
            },
            "right":{  
            "function":c_Right,
            "argc":1,
            "desc":"Fly right for 'x' cm. x = [20,500]"
            },
            "forward":{  
            "function":c_Forward,
            "argc":1,
            "desc":"Fly forward for 'x' cm. x = [20,500]"
            },
            "back":{  
            "function":c_Back,
            "argc":1,
            "desc":"Fly backward for 'x' cm. x = [20,500]"
            },
            "cw":{  
            "function":c_Cw,
            "argc":1,
            "desc":"Rotate 'x' degrees clockwise. x = [1,360]"
            },
            "ccw":{  
            "function":c_Ccw,
            "argc":1,
            "desc":"Rotate 'x' degrees counterclockwise. x = [1,360]"
            },
            "flip":{  
            "function":c_Flip,
            "argc":1,
            "desc":"Flip in 'x' direction. 'l' = left 'r' = right 'f' = forward 'b' = back"
            },
            "go":{  
            "function":c_Go,
            "argc":4,
            "desc":"Fly to 'x' 'y' 'z' at 'speed' (cm/s). " +
            "'x' = [-500,500] 'y' = [-500,500] 'z' = [-500,500] " + 
            "'speed' = [10,100]"
            },
            "stop":{  
            "function":c_Stop,
            "argc":0,
            "desc":"Hovers in the air. Note: works at any time."
            },
            "curve":{  
            "function":c_Curve,
            "argc":7,
            "desc":"Fly at a curve according to the two given coordinates."
            },
            "speed":{  
            "function":c_Speed,
            "argc":1,
            "desc":"Set speed to 'x' cm/s. x = [10,100]"
            },
            
    };
    

    // Given a Telsim API command, will return the corresponding Javascript 
    // function and an array of arguments to be passed to the function.
    // Ex:
    // Translate("speed 10") -> {"function": c_Speed, "argv": [10]}
    static Translate(command)
    {
        if(typeof command !== "string")
        {
            throw("Execute must be passed a String");
        }

        // Split the command on whitespace so that
        // we can work with multiple parameters
        var commandBuff = command.split(" ");
        
        var rootCommand = commandBuff[0];

        var commandData = TelloTranslate.commandMap[rootCommand];

        // We will only check if there are not enough arguments provided for 
        // the desired command. We will not check if we are given too many.
        // If there are more arguments provided than neccessary, we will use the
        // first n arguments where n is the expected number of arguments. 
        if(commandBuff.length < commandData.argc + 1)
        {
            throw(
                "Invalid Command: '" + command + "' (Argument Count Mismatch," +
                " Expecting " + String(commandData.argc) + " arguments)"
            );
        }

        var rtnObj = 
        {
            "function": commandData.function,
            "argv": commandBuff.slice(1)
        };

        return rtnObj;
    }
};