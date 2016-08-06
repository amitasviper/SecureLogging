var socket = io.connect('http://' + document.domain + ':' + location.port);
function get_data(){

    socket.emit('channel_all_ppls_req', 'ready');

    socket.on('channel_all_ppls_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got data : ' + data);

        data = JSON.parse(data);

        console.log('Got data rrwr: ' + typeof(data));

        $.each(data, function (index, value) {
          console.log(value.from_ip + " " + value.encrypted_log + " " + value.hash );
          //actual_data = actual_data.replace(/'/g, '"');
          //actual_data = JSON.parse(JSON.stringify(actual_data));
          //actual_data = JSON.parse(actual_data);
          var signature = value.signature;
          if(signature.length > 10) signature = signature.substring(0,10)+"...";
          $('#table_ppls').append('<tr><td>' + index + '</td><td>' + value.ip +'</td><td>' + value.time_of_ppl_generation + '</td><td id = "id" onclick="get_ppl_details(\'from_ip=' + value.ip +'&start_date=' + value.time_of_ppl_generation +'\')"><a>' + signature + '</a></td></tr>');
        });
    });
}

function get_logs(){
    
    var base_uri = document.baseURI;
    base_uri = base_uri.split("?")[1]

    socket.emit('channel_log_req', base_uri);

    socket.on('channel_log_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got data : ' + data);

        data = JSON.parse(data);

        $.each(data, function (index, value) {
          //actual_data = actual_data.replace(/'/g, '"');
          //actual_data = JSON.parse(JSON.stringify(actual_data));
          //actual_data = JSON.parse(actual_data);
          var elog = value.encrypted_log;
          if(elog.length > 10) elog = elog.substring(0,10)+"...";
          $('#table_logs').append('<tr id="' + index + '"><td style="vertical-align:middle">' + index +'</td><td style="vertical-align:middle">'+ value.from_ip + '</td><td>' + value.hash +'</td><td>' + elog +'</td><td>'+ value.time +'</td></tr>')
        });
    });
}

function generatePPLs()
{
    socket.emit('channel_function_request', 1);
}

function generateLogs()
{
    socket.emit('channel_function_request', 2);
}

function clearPPLs()
{
    socket.emit('channel_function_request', 3);
}

function clearLogs()
{
    socket.emit('channel_function_request', 4);
}

function clearAll()
{
    socket.emit('channel_function_request', 5);
}

function get_ppl_details(ppl_details) {
    window.location.href = '/getppldetails?' + ppl_details;
}

function initialise(){
    get_data();
    get_logs();
}

function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise);