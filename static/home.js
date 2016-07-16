function get_data(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('channel_logs_req', 'ready');

    socket.on('channel_logs_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got data : ' + data);

        data = JSON.parse(data);

        console.log('Got data rrwr: ' + typeof(data));

        $.each(data, function (index, value) {
          console.log(value.from_ip + " " + value.encrypted_log + " " + value.hash );
          actual_data = value.actual_data;
          //actual_data = actual_data.replace(/'/g, '"');
          //actual_data = JSON.parse(JSON.stringify(actual_data));
          //actual_data = JSON.parse(actual_data);
          console.log(actual_data + " *** " + typeof(actual_data));
          var signature = value.signature;
          if(signature.length > 10) signature = signature.substring(0,10)+"...";
          $('#table_logs').append('<tr><td>' + index + '</td><td>' + actual_data.ip +'</td><td>' + actual_data.time_of_ppl_generation + '</td><td id = "id" onclick="get_ppl_details(\'from_ip=' + actual_data.ip +'&date=' +actual_data.time_of_ppl_generation +'\')"><a>' + signature + '</a></td></tr>');
        });
    });
}

function get_ppl_details(ppl_details) {
    window.location.href = '/getppldetails?' + ppl_details;
}

function initialise(){
    get_data();
}

function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise);