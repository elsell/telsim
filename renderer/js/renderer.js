let SHOW_FPS = true;
let COPTER_POS = { x: 0, y: 0, z: 0 };
let COPTER_SCALE = .07;
let COPTER_MODEL_SCALE = .321;
let COPTER_SPEED = 1;
let COPTER_DEST = { x: 3, y: -3, z: 5 };

// How many pixels represent 1 foot
let ONE_FOOT = 20;

// Length of one side of the square floor (feet)
let FLOOR_SIZE = 11;




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
    translate
    (
        COPTER_POS.x * ONE_FOOT,
        COPTER_POS.y * ONE_FOOT,
        COPTER_POS.z * ONE_FOOT
    );


    scale((COPTER_SCALE));
    model(COPTER_MODEL);
    pop();
}

function InterpolatePosition()
{
    var fps = frameRate();

    var distanceToTravel = 1 / fps * COPTER_SPEED;

    if
    (
        COPTER_POS.x > COPTER_DEST.x - distanceToTravel &&
        COPTER_POS.x < COPTER_DEST.x + distanceToTravel &&
        COPTER_POS.y > COPTER_DEST.y - distanceToTravel &&
        COPTER_POS.y < COPTER_DEST.y + distanceToTravel &&
        COPTER_POS.z > COPTER_DEST.z - distanceToTravel &&
        COPTER_POS.z < COPTER_DEST.z + distanceToTravel 
    )
    {
        return; 
    }

    var direction = createVector
    (
        COPTER_DEST.x - COPTER_POS.x,
        COPTER_DEST.y - COPTER_POS.y,
        COPTER_DEST.z - COPTER_POS.z
    );

    direction.normalize();

    direction.mult(distanceToTravel);

    COPTER_POS.x += direction.x;
    COPTER_POS.y += direction.y;
    COPTER_POS.z += direction.z;



}

function drawFloor()
{
    var newOneFoot = ONE_FOOT ;
    push();
    strokeWeight(0);

    push();
    translate(0,0,1);
    rectMode(RADIUS); 
    fill("#FF0000"); 
    rect(0, 0, newOneFoot * .5, .5 * newOneFoot);
    pop();

    // Translate so that the copter lies in the middle of 
    // the floor.
    translate(FLOOR_SIZE * newOneFoot * -.5 + newOneFoot * .5, FLOOR_SIZE * newOneFoot * -.5 + newOneFoot * .5)

    for(var x = 0; x < FLOOR_SIZE; x++)
    {
        for(var y = 0; y < FLOOR_SIZE; y++)
        {
            push();
            if((x + y) % 2)
            {
                fill("white");
            }else { fill("grey"); }

            translate(x * newOneFoot, y * newOneFoot, 0);
            plane(newOneFoot, newOneFoot);
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

    InterpolatePosition();

    drawCopter();

}