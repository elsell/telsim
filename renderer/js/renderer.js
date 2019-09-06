let SHOW_FPS = true;
let SHOW_GROUND_MARKER = true;

let COPTER_POS = { x: 0, y: 0, z: 0 };
let COPTER_DEST = { x: 0, y: 0, z: 0 };

let COPTER_SCALE = .068;
let COPTER_MODEL_SCALE = .321;
let COPTER_SPEED = 1;

let CAMERA_POS = { x:0, y: 0, z: 1000 };
let CAMERA_FOCUS = { x:0, y: 0, z: 0 };
let CAMERA_DEST = CAMERA_POS;
let CAMERA_SPEED = 1250;

let VIEWS = 
{
    topView:    { x:0, y: 0, z: 1000 },
    sideView:   { x:0, y: 1100, z: 350 },
    cornerView: { x:1000, y: 200, z: 1000 }
};

let COMMANDS = [];

// How many pixels represent 1 foot
let ONE_FOOT = 20;

// Length of one side of the square floor (feet)
let FLOOR_SIZE = 11;

let COPTER_MODEL;
let FONT; 

function preload()
{
    COPTER_MODEL = loadModel('assets/copter.stl');
    FONT = loadFont('assets/incosolata.ttf');
}

// Runs once
function setup()
{
    createCanvas(windowWidth, windowHeight, WEBGL);
    textSize(20);
    textAlign(TOP, LEFT);

    textFont(FONT);
    
    windowResized();
}


function windowResized() 
{
    var smallestDimension = windowWidth;

    if(windowHeight < smallestDimension){ smallestDimension = windowHeight; }

    var floorWidth = smallestDimension;

    ONE_FOOT = floorWidth / FLOOR_SIZE;

    resizeCanvas(windowWidth, windowHeight);
}

function drawFps()
{
    if(SHOW_FPS)
    {
        if(frameCount % 15 == 0)
        {
            let fps = frameRate();
            $("#fps").text("FPS: " + fps.toFixed(0));
        }
    }
}

function drawCopter()
{
    push();

    translate
    (
        COPTER_POS.x * ONE_FOOT,
        COPTER_POS.y * ONE_FOOT,
        COPTER_POS.z * ONE_FOOT + 1
    );

    if(SHOW_GROUND_MARKER)
    {
        push();
        fill("red");
        strokeWeight(0);
        translate(0, 0, COPTER_POS.z  * -ONE_FOOT);
        box(10,10,1);
        pop();
    }



    scale(COPTER_SCALE * (1/65) * ONE_FOOT);
    model(COPTER_MODEL);
    pop();
}

function DrawAxes()
{
    var coneRadius = ONE_FOOT * .1;
    var coneLength = ONE_FOOT * .5;
    
    push();
    translate
    (   
        FLOOR_SIZE * ONE_FOOT * -.5,
        FLOOR_SIZE * ONE_FOOT * .5 - ONE_FOOT * .75,
        0
    );

    strokeWeight(0);
    
    // Y (north)
    push();
    rotateZ(PI);
    fill("green");
    cone(coneRadius, coneLength);
    translate(0, -coneLength, 0);
    cylinder(coneRadius * .1, coneLength)
    pop();

    // X (east)
    push();
    translate(coneLength * 1.5, coneLength * 1.5, 0);
    rotateZ(-PI * .5);
    fill("red");
    cone(coneRadius, coneLength);
    translate(0, -coneLength, 0);
    cylinder(coneRadius * .1, coneLength)
    pop();

    // Z (up)
    push();
    translate(0, coneLength * 1.5, coneLength * 1.5);
    rotateZ(-PI * .5);
    rotateX(PI * .5);
    fill("blue");
    cone(coneRadius, coneLength);
    translate(0, -coneLength, 0);
    cylinder(coneRadius * .1, coneLength)
    pop();

    pop();
}

function CopterInPosition(curPos, destPos, speed)
{
    var fps = frameRate();
    var distanceToTravel = 1 / fps * speed;

    return(
        curPos.x > destPos.x - distanceToTravel &&
        curPos.x < destPos.x + distanceToTravel &&
        curPos.y > destPos.y - distanceToTravel &&
        curPos.y < destPos.y + distanceToTravel &&
        curPos.z > destPos.z - distanceToTravel &&
        curPos.z < destPos.z + distanceToTravel 
    );

}

// Increments curPos according to the speed provided
function InterpolatePosition(curPos, destPos, speed)
{
    var fps = frameRate();

    var distanceToTravel = 1 / fps * speed;

    if(CopterInPosition(curPos, destPos, speed))
    {
        return; 
    }

    var direction = createVector
    (
        destPos.x - curPos.x,
        destPos.y - curPos.y,
        destPos.z - curPos.z
    );

    direction.normalize();

    direction.mult(distanceToTravel);

    curPos.x += direction.x;
    curPos.y += direction.y;
    curPos.z += direction.z;
}

function drawFloor()
{
    push();
    strokeWeight(0);

    push();
    translate(0,0,.1);
    rectMode(RADIUS); 
    fill("#FF0000"); 
    rect(0, 0, ONE_FOOT * .5, .5 * ONE_FOOT);
    pop();

    // Translate so that the copter lies in the middle of 
    // the floor.
    translate
    (   
        FLOOR_SIZE * ONE_FOOT * -.5 + ONE_FOOT * .5,
        FLOOR_SIZE * ONE_FOOT * -.5 + ONE_FOOT * .5
    );

    for(var x = 0; x < FLOOR_SIZE; x++)
    {
        for(var y = 0; y < FLOOR_SIZE; y++)
        {
            push();
            if((x + y) % 2)
            {
                fill("white");
            }else { fill("grey"); }

            translate(x * ONE_FOOT, y * ONE_FOOT, 0);
            plane(ONE_FOOT, ONE_FOOT);
            pop();
        }
    }

    pop();
}

function UpdateCamera()
{
    camera(CAMERA_POS.x, CAMERA_POS.y, CAMERA_POS.z,
        CAMERA_FOCUS.x, CAMERA_FOCUS.y, CAMERA_FOCUS.z,
        0, 1, 0);
}

function SetLighting()
{
    ambientLight(255);
    ambientMaterial(255);

}

function HandleCommands()
{
    if(!CopterInPosition(COPTER_POS, COPTER_DEST, COPTER_SPEED)) { return; }
    
    var curCmd = COMMANDS.pop();

    if(!curCmd) { return; }

    curCmd.Execute();
}

// Called every frame
function draw()
{
    SetLighting();

    InterpolatePosition(CAMERA_POS, CAMERA_DEST, CAMERA_SPEED);

    UpdateCamera();

    background("#AFAFAF");

    drawFps();

    DrawAxes();

    drawFloor();

    HandleCommands();

    InterpolatePosition(COPTER_POS, COPTER_DEST, COPTER_SPEED);

    drawCopter();
}