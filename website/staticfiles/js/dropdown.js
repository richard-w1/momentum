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

// Mark as important event trigger
$(document).ready(function() {
    $(".is_important").click(function(eve){
        // searches for the favourite star icon
        var starIcon = $(this).find("i.favourite-star");
        // toggling between the icons
        starIcon.toggleClass("far fas");
        starIcon.toggleClass("marked unmarked");
    });
});

// hide and display add-tags pop-up trigger
$(document).ready(function() {
    $(".pop-up-button").click(function(eve){   
        
        // closing all other pop in case one is already open
        $(".pop-up.open").removeClass("open");

        //only adds the class for the current div
        $(this).siblings(".pop-up").addClass("open");

        // stops the trigger after the first instance
        eve.stopPropagation(); 
    });

    // hides the pop-up only when visible
    $(document).click(function(eve){
        
        // checking if visible
        if ($(".pop-up").hasClass("open")){
            
            // hiding the pop-up
            $(".pop-up").removeClass("open");
        }
    });

    // ignoring the clicks inside the pop-up
    $('.pop-up').click(function(e){
        e.stopPropagation();
    });
});