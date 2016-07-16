
var memory_series, cpu_series, network_series;
var friendly_name = {'cpu_stats': 'CPU Usage', 'memory_stats' : 'Memory Usage', 'network_stats' : 'Network Usage'};
var socket, cpu_count=1;
function get_data(var_url)
{
    //console.log("calling for : " + json_key);
    var count = 0;
        socket.emit('channel_container_info_stream', container_id);

		socket.on('channel_container_info_stream'+"_"+container_id, function (data)
        {
            show('page', true);
            show('loading', false);

            data = JSON.parse(data);
            //console.log(data);

			x = (new Date()).getTime(); // current time

            //for cpu graph
            var flag1 = false;
            var flag2 = false;

            //console.log("CPU values ALL : " + data.cpu_stats.cpu_usage.percpu_usage);
            for(i = 0; i < cpu_series.length; i++)
            {
                if(i == cpu_series.length - 1)
                {
                        flag1 = true;
                        flag2 = true;
                }
                z = data.cpu_stats.cpu_usage.percpu_usage[i];
                //console.log("CPU values are : " + x + "  "+ z);
                cpu_series[i].addPoint([x, z], flag1, cpu_series[i].data.length >= cpu_series[0].data.length ? true : false);
            }

            //for memory graph
            y = data.memory_stats.usage;
            //console.log("The x and y values are : " + x + "  "+ y);
            memory_series[0].addPoint([x, y], true, true);

            y = data.networks.eth0.rx_bytes;
            //console.log("The x and y values are : " + x + "  "+ y);
            network_series[0].addPoint([x, y], false, true);

            y = data.networks.eth0.rx_bytes;
            //console.log("The x and y values are : " + x + "  "+ y);
            network_series[1].addPoint([x, y], true, true);


            //for network usage graph
            //empty for the time being

/*			if(json_key == 'cpu_stats'){
                //console.log("The cpu_usage array is : " + JSON.stringify(data));
                var flag = false;
                var flag2 = false;
                for(i = 0; i < var_series.length; i++){
                    if(i == var_series.length - 1){
                        flag = true;
                        flag2 = true;
                    }
                    z = data.cpu_usage[i];
                    var_series[i].addPoint([x, z], flag, var_series[i].data.length >= var_series[0].data.length ? true : false);
                }
			}
            else{
                y = data[json_key];
                console.log("The x and y values are : " + x + "  "+ y);
                var_series[0].addPoint([x, y], true, true);
            }*/
            
			//console.log("Series : "+var_series[0])
			//get_data(var_url);

            /*count += 1;
            if(count > 5)
            {
              socket.emit('channel_container_one_req', 'stillconnected');
              count = 0;
            }*/


		});
		/*error: function(status, error)
        {
			x = (new Date()).getTime(); // current time
			y = 0;

			//for cpu graph
            var flag1 = false;
            var flag2 = false;
            for(i - 0; i < cpu_series.length; i++)
            {
                if(i == cpu_series.length - 1)
                {
                        flag1 = true;
                        flag2 = true;
                }
                cpu_series[i].addPoint([x, y], flag1, cpu_series[i].data.length >= cpu_series[0].data.length ? true : false);
            }

            //for memory graph
            console.log("The x and y values are : " + x + "  "+ y);
            memory_series[0].addPoint([x, y], true, true);


			console.log("Into error");
			setTimeout(function(){get_data(var_url)}, 2000);
		}*/
}

function initialise_graphs(){
    console.log("Into the initialise phase");
    render_chart("#memory_usage_chart", memory_series, 'memory_stats');
    render_chart("#cpu_usage_chart", cpu_series, 'cpu_stats');
    render_chart("#network_usage_chart", network_series, 'network_stats');

    url = '/container_stats_stream/' + container_id;
    get_data(url);
}

function initialise(){
    show('page', false);
    show('loading', true);

    console.log("The container id is :" +container_id);
    socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('channel_container_info_json', container_id);
    socket.on('channel_container_info_json', function (data)
    {
        console.log(data);
        if(data == 'false')
        {
            show('page', true);
            show('loading', false);
            show('charts', false);
            show('empty_response', true);

        }
        else
        {
            //data = JSON.parse(data);
            cpu_count = data.cpu_stats.cpu_usage.percpu_usage.length;
            initialise_graphs();
        }
        
    });
}


function render_chart(container_name, series_name, json_key) {
    $(document).ready(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });

        $(container_name).highcharts({
            chart: {
                type: 'spline',
                animation: true, // don't animate in old IE
                marginRight: 10,
                events: {
                    load: function () {
                        // set up the updating of the chart each second
                        if(json_key == 'cpu_stats')
                        {
                            cpu_series = this.series;
                        }
                        else if( json_key == 'memory_stats')
                        {
                            memory_series = this.series;
                        }
                        else if (json_key == 'network_stats') 
                        {
                            network_series = this.series;
                        };
                        console.log("Size of the series " + this.series + " is : " + this.series.length);
                    }
                }
            },
            title: {
                text: friendly_name[json_key]
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {
                    text: 'Value'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            exporting: {
                enabled: false
            },
            series: create_series_array(json_key)
        });
    });
}

function create_series_array(json_key){
	var size = 1;
    console.log("Generating series for " + json_key);
	if (json_key == 'cpu_stats')
    {
		size = cpu_count;
    }

    else if (json_key == 'network_stats') 
    {
        size = 2;
    };

    var temp_series = [];
    for (j = 0; j <size; j += 1){
        instance_series = {
            name: friendly_name[json_key] + ' #' + j,
            data: (function () {
                    // generate an array of random data
                    var data = [],
                        time = (new Date()).getTime(),
                        i;
            
                    for (i = -19; i <= 0; i += 1) {
                        data.push({
                            x: time + i * 1000,
                            y: Math.random()*100
                        });
                    }
                    return data;
                }())
            }
        temp_series[j] = instance_series;
    }
    return temp_series;
}


function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise);