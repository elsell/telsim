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
});