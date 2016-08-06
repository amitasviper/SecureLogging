async_mode = None

if async_mode is None:
	try:
		import eventlet
		async_mode = "eventlet"
	except ImportError:
		pass

	if async_mode is None:
		try:
			from gevent import monkey
			async_mode = 'gevent'
		except ImportError:
			pass

	if async_mode is None:
		async_mode = 'threading'

	print "async_mode is ", async_mode

if async_mode == 'eventlet':
	import eventlet
	eventlet.monkey_patch()
elif async_mode == 'gevent':
	from gevent import monkey
	monkey.patch_all()

import utils, dbhelper, os, unicodedata
from dummy_data import GetDummydata
import time, random, json, urllib2, requests
from flask import Flask, render_template, url_for, request, jsonify, Response, send_from_directory
from flask_socketio import SocketIO, send, emit

from threading import Thread

utils.DEBUG_LEVEL = 10

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)

connection = dbhelper.MConnection(debug=utils.DEBUG_LEVEL)


#Renders the home page of the application server.
@app.route('/')
@app.route('/home')
def home():
	#print url_for('static', filename='../js/statistics.js')
	return render_template('home.html', title="Home")


@app.route('/keys')
def keys():
	return render_template('downloadKeys.html', title="Download Keys")


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
	filepath = None
	if filename == "LEA":
		filepath = utils.get_key_path("LEA", "public")
	else:
		filepath = utils.get_key_path("CSP", "public")
	content = ""
	with open(filepath, 'r') as content_file:
		content = content_file.read()
	return Response(
        content,
        mimetype='application/octet-stream',
        headers={"Content-disposition":
                 "attachment; filename=" + filename +".pem"})

@app.route('/getppldetails')
def get_ppl_details():
	try:
		return render_template('ppldetails.html')
		#return render_template('ppldetails.html', ppl_info=json.dumps(response))
	except:
		return """<center>
			<h1 style="margin-top:100px;">Landed on a WRONG page. You must have left some field empty or entered incorrect value.<br> <a href='/'>HOME</a></h1>
			</center>
			"""

@app.route('/getlogs', methods=['GET', 'POST'])
def get_logs():
	#try:
	from_ip = request.args.get('from_ip')
	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')
	print from_ip, start_date, end_date
	if end_date == None:
		start_date = utils.ConvertStringToISODate(start_date)
		resp = connection.FetchPPL(from_ip, start_date)
		iso_time = resp['time']
		utc_time = iso_time.isoformat()
		resp['time'] = utc_time
		return render_template('logdetails.html')
		#return render_template('ppldetails.html', ppl_info=json.dumps(resp))
	else:
		start_date = utils.ConvertStringToISODate(start_date)
		end_date = utils.ConvertStringToISODate(end_date)
		cursor = connection.FetchLogsRange(from_ip, start_date, end_date)
		response = []
		for i in range(cursor.count()):
			current = cursor[i]
			iso_time = current['time']
			utc_time = iso_time.isoformat()
			current['time'] = utc_time
			response.append(current)
		return render_template('logdetails.html')
		#return render_template('ppldetails.html', ppl_info=json.dumps(response))
	#except:
	return """<center>
		<h1 style="margin-top:100px;">Landed on a WRONG page. You must have left some field empty or entered incorrect value.<br> <a href='/'>HOME</a></h1>
		</center>
		"""


def main():
	print "Thread started"

	global connection

	public_key = utils.Get_RSA_key("LEA", "public")

	cursor = connection.fetch_all()

	for i in range(200):
		log_entry = GetDummydata()
		print log_entry
		
		encrypted_log_entry = {}
		encrypted_log_entry['encrypted_log'] = utils.EncryptData(log_entry, public_key, dict_keys=['from_ip', 'to_ip', 'port','time'])
		encrypted_log_entry['from_ip'] = log_entry['from_ip']
		encrypted_log_entry['time'] = log_entry['time']

		print "Encrypted : ",encrypted_log_entry, "\n\n"
	

		#encrypted_log_entry is a dict
		connection.SaveLogEntryInDatabase(encrypted_log_entry)

		current = connection.get_current_accumulator(encrypted_log_entry['from_ip'])
	
		if current == None:
			bloom_filter = utils.BloomFilter(ip=encrypted_log_entry['from_ip'], capacity=200, error_rate=10)
	
		else:
			bloom_filter = utils.BloomFilter(bloom_dict=current)

		bloom_filter.AddToFilter(encrypted_log_entry['encrypted_log'])
		connection.update_accumulator(bloom_filter.Serialise())
	
	utils.GeneratePPL()

@socketio.on('channel_logs_req')
def channel_hosts_list(c_req):
	global socketio
	print "Client requested for logs"
	cursor = connection.FetchAllPPl()
	response = []
	for i in range(cursor.count()):
		current = cursor[i]
		print "*******", type(current)
		iso_time = current['time_of_ppl_generation']
		utc_time = iso_time.isoformat()
		current['time_of_ppl_generation'] = utc_time
		response.append(current)
	#print "Response : ", response
	print "Size of json_data : ", len(response)
	js = json.dumps(response)
	#print js
	socketio.emit('channel_logs_resp', js)

@socketio.on('channel_keys_req')
def channel_keys(c_req):
	global socketio
	print "Client requested for keys"
	cursor = connection.FetchAllPPl()
	response = []
	public = utils.Get_RSA_key("LEA", "public")
	res = {'AgencyName' : 'LEA', 'keyval' : public.exportKey()}
	response.append(res)
	public = utils.Get_RSA_key("CSP", "public")
	res = {'AgencyName' : 'CSP', 'keyval' : public.exportKey()}
	response.append(res)
	js = json.dumps(response)
	print js
	socketio.emit('channel_keys_resp', js)

@socketio.on('channel_ppl_req')
def channel_ppls(ppls_query):
	global socketio
	print "Client requested for ppls : ",ppls_query 

	from_ip, start_date, end_date = None, None, None

	ppls_query = ppls_query.split('&')
	if len(ppls_query) > 2:
		end_date = ppls_query[2][len("end_date="):]
	start_date = ppls_query[1][len("start_date="):]
	from_ip = ppls_query[0][len("from_ip="):]
	resp = []
	print "*****", from_ip, start_date, end_date
	if end_date == None:
		start_date = utils.ConvertStringToISODate(start_date)
		current = connection.FetchPPL(from_ip, start_date)
		iso_time = current['time_of_ppl_generation']
		utc_time = iso_time.isoformat()
		print type(current['signature'])
		#current['signature'] = unicodedata.normalize('NFKD', current['signature']).encode('ascii','ignore')
		print type(current['signature'])
		current['time_of_ppl_generation'] = utc_time
		resp.append(current)
	else:
		start_date = utils.ConvertStringToISODate(start_date)
		end_date = utils.ConvertStringToISODate(end_date)
		cursor = connection.FetchPPLsRange(from_ip, start_date, end_date)
		for i in range(cursor.count()):
			current = cursor[i]
			iso_time = current['time_of_ppl_generation']
			utc_time = iso_time.isoformat()
			current['time_of_ppl_generation'] = utc_time
			print type(current['signature'])
			#current['signature'] = unicodedata.normalize('NFKD', current['signature']).encode('ascii','ignore')
			print type(current['signature'])
			resp.append(current)
	socketio.emit('channel_ppl_resp', json.dumps(resp))

@socketio.on('channel_log_req')
def channel_logs(logs_query):
	global socketio
	print "Client requested for LOGS : ",logs_query 

	from_ip, start_date, end_date = None, None, None

	logs_query = logs_query.split('&')
	if len(logs_query) > 2:
		end_date = logs_query[2][len("end_date="):]
	start_date = logs_query[1][len("start_date="):]
	from_ip = logs_query[0][len("from_ip="):]
	resp = []
	from_ip = None
	print "*****", from_ip, start_date, end_date
	if end_date == None:
		start_date = utils.ConvertStringToISODate(start_date)
		current = connection.FetchLogsRange(from_ip, start_date)
		iso_time = current['time']
		utc_time = iso_time.isoformat()
		current['time'] = utc_time
		resp.append(current)
	else:
		start_date = utils.ConvertStringToISODate(start_date)
		end_date = utils.ConvertStringToISODate(end_date)
		cursor = connection.FetchLogsRange(from_ip, start_date, end_date)
		for i in range(cursor.count()):
			current = cursor[i]
			iso_time = current['time']
			utc_time = iso_time.isoformat()
			current['time'] = utc_time
			resp.append(current)
	socketio.emit('channel_log_resp', json.dumps(resp))

@socketio.on('channel_ppl_verify_req')
def channel_ppls_verify(data):
	global socketio
	index, data = data.split("****")
	actual_data, sig = data.split("$####$")
	print actual_data, "\n",sig
	filepath = utils.get_key_path("CSP", "public")
	key_content = ""
	with open(filepath, 'r') as content_file:
		key_content = content_file.read()

	res = utils.VerifySignature(key_content, data, sig)

	socketio.emit('channel_ppl_verify_resp'+index, res)

@socketio.on('channel_log_verify_req')
def channel_log_verify(data):
	global socketio
	data = unicodedata.normalize('NFKD', data).encode('ascii','ignore')
	data = data[:-3]
	print data
	logs_arr = data.split(",,,")
	i = 0
	flag = True
	while i < len(logs_arr)-1:
		prev_dble = {}
		current_dble = {}

		prev = logs_arr[i].split("***")
		prev_dble['encrypted_log'] = prev[0]
		prev_dble['hash'] = prev[1]
		i += 1

		cur = logs_arr[i].split("***")
		current_dble['encrypted_log'] = cur[0]
		current_dble['hash'] = cur[1]

		print '\n\n',prev_dble,'\n\n' ,current_dble, '\n\n'
		flag = utils.SequenceVerification(prev_dble, current_dble)
		if flag == False:
			break
	
	socketio.emit('channel_log_verify_resp', flag)

if __name__ == "__main__":

	#thread = Thread(target=main)
	#thread.start()

	socketio.run(app, '', port=4000, debug=True)
