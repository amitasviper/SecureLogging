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
          $('#table_log_details').append('<tr id="' + index + '"><td style="vertical-align:middle">' + index +'</td><td style="vertical-align:middle"><input type="text" id="ip' + index + '" class="form-control" value="' + value.from_ip + '"/><br><input type="text" class="form-control" id="time' + index+ '" value="' + value.time + '"/></td><td><p>Encrypted Log:</p><textarea class="form-control" id="elog' + index + '" cols="130" rows="4" >' + value.encrypted_log +'</textarea><br><p>Log Hash Chain:</p><textarea id="hash' + index + '" class="form-control" cols="130" rows="1" >' + value.hash +'</textarea><div style="display:none;" id="raw_data_div' + index + '"><br>Decrypted Data :<textarea class="form-control" style="background-color:#D4EFDF;" id="raw_data' + index +'" cols="130" rows="4"></textarea></div></td><td><button class="' + index + 'btn btn btn-primary" onclick="addToChain(' + index + ')">Add to Chain</button><br><br><button id="inaccumulator' + index +'" class="' + index + 'abtn btn btn-info" onclick="isInAccumulator(' + index + ')">Test if in Acc</button><br><br><button class="' + index + 'dbtn btn btn-warning" onclick="decrypt(' + index + ')">Decrypt Data</button></td></tr>')
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

  var button = document.getElementById('inaccumulator'+index);
  
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

function decrypt(index)
{
  var elog = document.getElementById('elog'+index).value;

  data = elog + "***" + index;

  socket.emit('channel_log_dec_req', data);

  socket.on('channel_log_dec_resp' + index, function (data) {

  data = JSON.stringify(data);

  var raw_data_div = document.getElementById('raw_data_div'+index);
  raw_data_div.style.display = 'block';

  var raw_data = document.getElementById('raw_data'+index);
  raw_data.textContent = data;

  });

}

function addToChain(index)
{
  //var n = el.parentNode.parentNode.cells[2].getElementByClassName('accumulator');
  var row = $("#" + index);
  var elog  = document.getElementById('elog'+index).value;
  var hash_chain = document.getElementById('hash'+index).value;
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

$(document).ready(initialise);