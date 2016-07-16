function setActive() {
  get_connected_hosts();
	var tag_object = document.getElementById('cssmenu').getElementsByTagName('a');

  	var base_url = getBaseURL();					// -> http://localhost:3000
  	var base_url_length = base_url.length;			// -> 21
  	var absolute_page_url = window.location.href;	// -> http://localhost:3000/container/asd


  	var relative_page_url = absolute_page_url.substr(base_url_length+1, absolute_page_url.length);	// -> container/asd
  	var page_name = relative_page_url.substr(0, relative_page_url.indexOf('/'));			// -> container

  	//console.log("base_url: " + base_url + " absolute_page_url: " + absolute_page_url + " relative_page_url: " + relative_page_url + " page_name: " + page_name );

  	for( i=0; i<tag_object.length; i++) { 
  		var absolute_tag_url = tag_object[i].href;
  		var relative_tag_url = absolute_tag_url.substr(base_url_length+1, absolute_tag_url.length);
  		var tag_name = relative_tag_url.substr(0, relative_tag_url.indexOf('/'));
  		
  		//console.log("Comparing : " + tag_name + " Page Name : " + page_name);
    
    	if(tag_name==page_name) {
      		tag_object[i].parentElement.className='active';
    	}
    	else{
    		tag_object[i].parentElement.className='none';
    	}
  	}
}

function getBaseURL() {
        return location.protocol + "//" + location.hostname + (location.port && ":" + location.port);
}

function get_connected_hosts(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('channel_hosts_list_req_1', 'ready');

    socket.on('channel_hosts_list_resp_1', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        //console.log('Got container_id : ' + data);

        data = JSON.parse(data);
        var base_url = window.location.href;
        var url_arr = base_url.split("/");
        var result = url_arr[0] + "//" + url_arr[2] + "/static/pc.png";

        $.each(data, function (index, value) {
          $('#sidebar_hosts').append('<li id = "id"><img height="40" width="40" src="' + result +'"><a href="javascript:host_info(\'' + value.ip + '\')"><font size="5">' + value.ip + '</font></a></li>');
        });
    });
}

function host_info(id) {
    window.location.href = '/host/' + id;
}

window.onload = setActive();
