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
    make_graph(data)
})

function make_graph(data){
    const ctx = document.getElementById('chart');
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
            labels: Object.keys(data),
            datasets: [{
            label: 'number of habits',
            data: Object.values(data),
            borderWidth: 1
            }]
        },
        options: {

        }
    });
}