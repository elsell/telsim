$(document).ready(()=>
{
    $("#top").on("click", ()=>
    {
        CAMERA_POS = VIEWS.topView;
    });

    $("#side").on("click", ()=>
    {
        CAMERA_POS = VIEWS.sideView;
    });

    $("#corner").on("click", ()=>
    {
        CAMERA_POS = VIEWS.cornerView;
    });
});