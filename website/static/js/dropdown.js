$(document).ready(function() {
    // initially hiding all the items
    $('.habit-item').hide()
    
    // toggling the display on click and
    // swapping the unicode triangle
    $(".dropdown-menu").click(function(eve){
        eve.preventDefault();
        $(this).toggleClass("down");
        $('.habit-item').toggle();
    });
});
