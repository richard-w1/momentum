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
    make_daily_habit_graph(data)
    make_weekly_habit_graph(data)
    make_monthly_habit_graph(data)
})

function make_daily_habit_graph(data){
    const ctx = document.getElementById('daily_habit_chart');
    new Chart(ctx, {
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
    const ctx = document.getElementById('weekly_habit_chart');
    new Chart(ctx, {
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
    const ctx = document.getElementById('monthly_habit_chart');
    new Chart(ctx, {
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