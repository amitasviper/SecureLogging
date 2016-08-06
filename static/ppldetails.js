var socket = io.connect('http://' + document.domain + ':' + location.port);
function get_ppls(){
    
    var base_uri = document.baseURI;
    base_uri = base_uri.split("?")[1]

    socket.emit('channel_ppl_req', base_uri);

    socket.on('channel_ppl_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got data : ' + data);

        data = JSON.parse(data);

        console.log('Got data rrwr: ' +  data);

        $.each(data, function (index, value) {
          //actual_data = actual_data.replace(/'/g, '"');
          //actual_data = JSON.parse(JSON.stringify(actual_data));
          //actual_data = JSON.parse(actual_data);
          $('#table_ppl_details').append('<tr id="' + index + '"><td>' + index +'</td><td><input type="text" class="form-control" value="' + value.ip + '"/></td><td><p>Accumulator Data:</p><textarea class="form-control" class="accumulator" cols="130" rows="2" >' + value.actual_data +'</textarea><br><br><p>Signature Value:</p><textarea class="form-control" cols="130" rows="4" >' + value.signature +'</textarea></td><td><button class="' + index + 'btn btn btn-primary" onclick="rowFunction(' + index + ')">Verify Signature</button></td></tr>')
        });
    });
}

function rowFunction(index)
{
  //var n = el.parentNode.parentNode.cells[2].getElementByClassName('accumulator');
  var row = $("#" + index);
  var actual_data = row.children()[2].childNodes.item(1).value;
  var signature = row.children()[2].childNodes.item(5).value;
  console.log("Index is " + index + " Accumulator : " + actual_data + " Signature : " + signature);
  Verify_PPL(actual_data, signature, index);
}

function initialise(){
    get_ppls();
}

function Verify_PPL(actual_data, signature, index)
{
  var data = actual_data + "$####$" + signature;
  socket.emit('channel_ppl_verify_req', index + "****" +data);

  socket.on('channel_ppl_verify_resp' + index, function (data) {
  console.log(data);
  
  var row = $("#" + index);
  var button = row.children()[3].childNodes.item(0);
  console.log(button + typeof(button));

  if(button.className.split(" ")[0] == index+"btn"){
    if (data){
      button.className = index + "btn btn btn-success";
      button.textContent = "Success";
    }
    else{
      button.className = index + "btn btn btn-danger";
      button.textContent = "Failed";
    }
  }

  });
}
/*
function verify_signature(){
  $.ajax({
      type: 'GET',
      //async: false,
      url: var_url,
      dataType: 'json',
    success: function(data){
            show('page', true);
            show('loading', false);

      x = (new Date()).getTime(); // current time
      if(json_key == 'cpu_usage'){
                console.log("The cpu_usage array is : " + JSON.stringify(data));
                var flag = false;
                for(i = 0; i < var_series.length; i++){
                    if(i == var_series.length - 1){
                        flag = true;
                    }
                    z = data.cpu_usage[i];
                    var_series[i].addPoint([x, z], flag);
                }
      }
            else{
                y = data.json_key;
                var_series[0].addPoint([x, y], true);
            }
      console.log("Series : "+var_series[0])
      get_data(var_series, var_url, json_key);
    },
    error: function(status, error){
      x = (new Date()).getTime(); // current time
      y = 0;
      if(json_key == 'cpu_usage'){
        var_series[1].addPoint([x, Math.random()], true, true);

      }
      var_series[0].addPoint([x, y], true, true);
      console.log("Into error");
      setTimeout(function(){get_data(var_series, var_url, json_key)}, 2000);
    }
  });
} */

$(document).ready(initialise);