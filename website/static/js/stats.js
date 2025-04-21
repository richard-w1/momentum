let currentChart = null

// for daily weekly monthly progress charts

// getting the data form the /get_stats/ which runs 
// the get_stat view returning a json response
fetch('/get_stats/', {
    headers:{
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
    },
})
.then(response => {
    return response.json() //Convert response to JSON
})
.then(data => {
    $(document).ready(function() {
        $(".progress_report_frequency").change(function () {
            
            if (currentChart !== null) {
                currentChart.destroy();
            }

            // calling the proper funtion based on the option selected
            if ($(this).val() == "Daily") {
                make_daily_habit_graph(data)
            }else if ($(this).val() == "Weekly") {
                make_weekly_habit_graph(data)
            }else{
                make_monthly_habit_graph(data)
            }
        });
        $(".progress_report_frequency").trigger("change");
    });
})

function make_daily_habit_graph(data){
    const ctx = document.getElementById('chart');
    currentChart = new Chart(ctx, {
        type: 'pie',
        options: {
            animation: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                },
            }
        },
        data: {
            labels: Object.keys(data["daily_habit_stat"]),
            datasets: [{
            label: 'number of habits',
            data: Object.values(data["daily_habit_stat"]),
            borderWidth: 1
            }]
        },
        options: {

        }
    });
}

function make_weekly_habit_graph(data){
    const ctx = document.getElementById('chart');
    currentChart = new Chart(ctx, {
        type: 'pie',
        options: {
            animation: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                },
            }
        },
        data: {
            labels: Object.keys(data["weekly_habit_stat"]),
            datasets: [{
            label: 'number of habits',
            data: Object.values(data["weekly_habit_stat"]),
            borderWidth: 1
            }]
        },
        options: {

        }
        
    });
}

function make_monthly_habit_graph(data){
    const ctx = document.getElementById('chart');
    currentChart = new Chart(ctx, {
        type: 'pie',
        options: {
            animation: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                },
            }
        },
        data: {
            labels: Object.keys(data["monthly_habit_stat"]),
            datasets: [{
            label: 'number of habits',
            data: Object.values(data["monthly_habit_stat"]),
            borderWidth: 1
            }]
        },
        options: {

        }
    });
}

// weekly habit report chart
fetch('/get_weekly_stats/', {
    headers:{
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
    },
})
.then(response => {
    return response.json() //Convert response to JSON
})
.then(data => {
    $(document).ready(function() {
        // calling the function once the document is ready
        weekly_report_graph(data)
    });
})

// creates and render the weekly report graph
function weekly_report_graph(data){
    const ctx = document.getElementById('weekly_chart');
    new Chart(ctx, {
        type: 'bar',
        options: {
            animation: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                },
            }
        },
        data: {
            labels: Object.keys(data),
            datasets: [{
            label: 'number of habits completed',
            data: Object.values(data),
            borderWidth: 1
            }]
        },
        options: {

        }
        
    });
}