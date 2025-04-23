$(document).ready(function() {
    // initially hiding all the items
    // $('.habit-item').hide()
    
    // toggling the display on click and
    // swapping the unicode triangle
    $(".dropdown-menu").click(function(eve){
        eve.preventDefault();
        $(this).toggleClass("down");
        $('.habit-item').toggle();
    });
});

$(document).ready(function() {
    $(".is_important").click(function(eve){
        // serches for the favourite star icon
        var starIcon = $(this).find("i.favourite-star");
        // toggling between the icons
        starIcon.toggleClass("far fas");
        starIcon.toggleClass("marked unmarked");
    });
});