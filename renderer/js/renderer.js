let SHOW_FPS = true;
let COPTER_POS = { x: 0, y: 0, z: 0 };
let COPTER_SCALE = .07;

// How many pixels represent 1 foot
let ONE_FOOT = 20;

// Length of one side of the square floor (feet)
let FLOOR_SIZE = 15;


let COPTER_MODEL;

function preload()
{
    COPTER_MODEL = loadModel('assets/copter.stl');
}

// Runs once
function setup()
{
    createCanvas(windowWidth, windowHeight, WEBGL);
    textSize(width / 3);
    textAlign(CENTER, CENTER);

    
    windowResized();
}


function windowResized() 
{
    floorWidth = windowWidth - 50;

    ONE_FOOT = floorWidth / FLOOR_SIZE;

    resizeCanvas(windowWidth, windowHeight);
}

function drawFps()
{
    if(SHOW_FPS)
    {
        push();
        let fps = frameRate();
        fill(255);
        stroke(0);
        text("FPS: " + fps.toFixed(2), 0,0);
        pop();
    }
}

function drawCopter()
{
    push();
    scale(COPTER_SCALE);
    model(COPTER_MODEL);
    pop();
}

function drawFloor()
{
    push();
    strokeWeight(0);

    push();
    translate(0,0,1);
    rectMode(RADIUS); 
    fill("#FF0000"); 
    rect(0, 0, ONE_FOOT * .5, .5 * ONE_FOOT);
    pop();

    // Translate so that the copter lies in the middle of 
    // the floor.
    translate(FLOOR_SIZE * ONE_FOOT * -.5 + ONE_FOOT * .5, FLOOR_SIZE * ONE_FOOT * -.5 + ONE_FOOT * .5)

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

// Called every frame
function draw()
{
    orbitControl();

    background("#AFAFAF");

    drawFps();

    drawFloor();

    // rotateX(frameCount * 0.01);
    // rotateY(frameCount * 0.01);

    drawCopter();

    push();

    pop();

}