$(document).ready(()=>
{
    $("#top").on("click", ()=>
    {
        CAMERA_DEST = VIEWS.topView;
    });

    $("#side").on("click", ()=>
    {
        CAMERA_DEST = VIEWS.sideView;
    });

    $("#corner").on("click", ()=>
    {
        CAMERA_DEST = VIEWS.cornerView;
    });

    $("#reset").on("click", ()=>
    {
        COPTER_DEST = { x: 0, y: 0, z: 0 }; 
    });
});