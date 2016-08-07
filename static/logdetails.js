var socket = io.connect('http://' + document.domain + ':' + location.port);
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
          $('#table_log_details').append('<tr id="' + index + '"><td style="vertical-align:middle">' + index +'</td><td style="vertical-align:middle"><input type="text" id="ip' + index + '" class="form-control" value="' + value.from_ip + '"/><input type="text" class="form-control" id="time' + index+ '" value="' + value.time + '"/></td><td><p>Encrypted Log:</p><textarea class="form-control" id="elog' + index + '" cols="130" rows="4" >' + value.encrypted_log +'</textarea><br><p>Log Hash Chain:</p><textarea class="form-control" cols="130" rows="1" >' + value.hash +'</textarea></td><td><button class="' + index + 'btn btn btn-primary" onclick="addToChain(' + index + ')">Add to Chain</button><br><br><button class="' + index + 'abtn btn btn-info" onclick="isInAccumulator(' + index + ')">Test if in Acc</button></td></tr>')
        });
    });
}

function isInAccumulator(index)
{
  var ip = document.getElementById('ip'+index).value;
  var elog = document.getElementById('elog'+index).value;
  var time = document.getElementById('time'+index).value;

  data = ip + "***" + elog + "***" + time + "***" + index;

  socket.emit('channel_log_inacc_req', data);

  socket.on('channel_log_inacc_resp' + index, function (data) {

    var row = $("#" + index);
    var button = row.children()[3].childNodes.item(3);
    console.log(button + typeof(button));
  
  if(data)
  {
    if(button.className.split(" ")[0] == index+"abtn"){
        button.className = index + "abtn btn btn-success";
        button.textContent = "Present";
    }
  }
  else
  {
    if(button.className.split(" ")[0] == index+"abtn"){
        button.className = index + "abtn btn btn-danger";
        button.textContent = "Not Present";
    }
  }

  });

}

function addToChain(index)
{
  //var n = el.parentNode.parentNode.cells[2].getElementByClassName('accumulator');
  var row = $("#" + index);
  var elog = row.children()[2].childNodes.item(1).value;
  var hash_chain = row.children()[2].childNodes.item(4).value;
  //Combine(actual_data, signature, index);

  var x = document.getElementById("query");
  x.value = x.value + elog + "***" + hash_chain + ",,,";


  var button = row.children()[3].childNodes.item(0);
  console.log(button + typeof(button));

  if(button.className.split(" ")[0] == index+"btn"){
      button.className = index + "btn btn btn-success";
      button.textContent = "Added";
  }

  var button = document.getElementById('btn-order');
  
    if(button.className.split(" ")[0] == "btn"){
        button.className = "btn btn btn-info";
        button.textContent = "Verify Sequence";
    }


}

function initialise(){
    get_logs();
}

function Verify_PPL(actual_data, signature, index)
{
    var x = document.getElementById("demo");
}


function checkOrder()
{
  var data = document.getElementById('query').value;

  console.log("Checking order");

  socket.emit('channel_log_verify_req', data);

  socket.on('channel_log_verify_resp', function (data) {

    var button = document.getElementById('btn-order');
  
    if(button.className.split(" ")[0] == "btn"){
      if (data){
        button.className = "btn btn btn-success";
        button.textContent = "Success";
      }
      else{
        button.className = "btn btn btn-danger";
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