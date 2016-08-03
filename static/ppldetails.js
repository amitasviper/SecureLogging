function get_keys(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('channel_keys_req', 'ready');

    socket.on('channel_keys_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got data : ' + data);

        data = JSON.parse(data);

        console.log('Got data rrwr: ' +  data);

        $.each(data, function (index, value) {
          //actual_data = actual_data.replace(/'/g, '"');
          //actual_data = JSON.parse(JSON.stringify(actual_data));
          //actual_data = JSON.parse(actual_data);
          $('#table_keys').append('<tr><td>' + index + '</td><td>' + value.AgencyName + '</td><td>' + value.keyval +'</td></tr>')
        });
    });
}

function initialise(){
    get_keys();
}


$(document).ready(initialise);