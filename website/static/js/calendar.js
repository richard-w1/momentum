document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',  
        eventDidMount: function(info){
            //getting the event
            var event = info.event;
            console.log("Event :", info.event.title);
            
            //getting all the completed dates for the event
            var completed_dates = event.extendedProps.completed_dates;
            console.log("Event completed date: ", completed_dates)
            
            //getting the start date of the event ignoreing the time
            var eventDate = event.start.toISOString().split('T')[0];
            console.log("Event date: ", eventDate)

            //getting today's date parsing out the time 
            var today = (new Date()).toISOString().split('T')[0];

            if(completed_dates &&completed_dates.includes(eventDate)){
                info.el.style.backgroundColor = 'green';;
            }else if(eventDate >= today){
                info.el.style.backgroundColor = 'light blue';;
            }else{
                info.el.style.backgroundColor = 'red';;
            }
        },
        events: '/get_habits/'
    });
    calendar.render();
});