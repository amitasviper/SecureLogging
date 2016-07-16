var chart_memory, chart_cpu, chart_network, chart_disk;
var socket;

var memory_data = [], cpu_data = [], network_data_sent = [], network_data_recv = [], disk_data = [];

var pc_count;

function requestData() {

  socket.emit('channel_compare_resources_req');

  socket.on('channel_compare_resources_resp', function (data)
  {
        data = JSON.parse(data);
    
        pc_count = data.length;
    
        for (var i = 0; i < data.length; i++)
        {
              var pc_data = data[i];
        
              x = (new Date()).getTime(); // current time
        
              y = pc_data.cpu;
              cpu_data[i] = y;
              //chart.series[0].data[i] = y;//addPoint(y, true, shift);
        
              y = pc_data.memory;
              memory_data[i] = y;
              //chart.series[1].data[i] = y;//addPoint(y, true, shift);
        
              y = pc_data.network;
              network_data_sent[i] = y.sent;
              network_data_recv[i] = y.recv;
              //chart.series[2].data[i] = y;//addPoint(y, true, shift);

              y = pc_data.disk;
              disk_data[i] = y;
    
        }
    
        console.log("requestData called : " + chart_cpu.series[0].data.length + " cpu_data " + cpu_data);
    
        chart_cpu.series[0].setData(cpu_data);
        chart_memory.series[0].setData(memory_data);
        chart_network.series[0].setData(network_data_sent);
        chart_network.series[1].setData(network_data_recv);
        chart_disk.series[0].setData(disk_data);
    
        chart_cpu.redraw();
        chart_memory.redraw();
        chart_network.redraw();
        chart_disk.redraw();

    });

    setInterval(function(){socket.emit('channel_compare_resources_req');}, 1000);
}

function render_chart() {

      var pc_names = [];
      var default_values = [];

      socket.emit('channel_compare_resources_init_req');
    
      socket.on('channel_compare_resources_init_resp', function (data)
      {
        console.log("Data received from server : " + data);
    
        data = JSON.parse(data);
        pc_data = data.length;
        for (var i = 0; i < data.length; i++)
        {
          pc_names.push(data[i].ip);
          default_values.push(0);

          memory_data.push(0);
          cpu_data.push(0);
          network_data_sent.push(0);
          network_data_recv.push(0);
        }
    
        console.log("PC names: " + pc_names);

        chart_cpu = new Highcharts.Chart({
            chart: {
                renderTo: 'compare_cpu_chart',
                type: 'column'
            },
            title: {
                text: 'CPU Comparison'
            },
            xAxis: {
                categories:pc_names,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Usage (%)'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                name: 'Cpu',
                data: default_values
    
            }]
        });
    
        //Memory Chart
    
        chart_memory = new Highcharts.Chart({
            chart: {
                renderTo: 'compare_memory_chart',
                type: 'column'
            },
            title: {
                text: 'Memory Comparison'
            },
            xAxis: {
                categories:pc_names,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Usage (%)'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                name: 'Memory',
                data: default_values
    
            }]
        });
    
    
        //Netwok Usage
        chart_network = new Highcharts.Chart({
            chart: {
                renderTo: 'compare_network_chart',
                type: 'column'
            },
            title: {
                text: 'Network Comparison'
            },
            xAxis: {
                categories:pc_names,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Usage (Bytes)'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} bytes</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                name: 'Sent',
                data: default_values
    
            },
            {
                name: 'Received',
                data: default_values
            }]
        });


        //Disk Chart
        chart_disk = new Highcharts.Chart({
            chart: {
                renderTo: 'compare_disk_chart',
                type: 'column'
            },
            title: {
                text: 'Disk Comparison'
            },
            xAxis: {
                categories:pc_names,
                crosshair: true
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Usage (%)'
                }
            },
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} %</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                name: 'Disk',
                data: default_values
    
            }]
        });
        


      requestData();

      });
}


function initialise_graphs(){
  console.log("Into the initialise phase");
  socket = io.connect('http://' + document.domain + ':' + location.port);
  render_chart();
}

function show(id, value) {
  document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise_graphs);