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


import utils, dbhelper
from dummy_data import GetDummydata
import time, random, json, urllib2, requests
from flask import Flask, render_template, url_for, request, jsonify, Response
from flask_socketio import SocketIO, send, emit

from threading import Thread

utils.DEBUG_LEVEL = 4

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)

connection = dbhelper.MConnection(debug=utils.DEBUG_LEVEL)


#Renders the home page of the application server.
@app.route('/')
@app.route('/home')
def home():
	#print url_for('static', filename='../js/statistics.js')
	return render_template('home.html', title="Home")

@app.route('/getppldetails', methods=['GET', 'POST'])
def get_ppl_details():
	try:
		from_ip = request.args.get('from_ip')
		start_date = request.args.get('start_date')
		end_date = request.args.get('end_date')
		print from_ip, start_date, end_date
		if end_date == None:
			start_date = utils.ConvertStringToISODate(start_date)
			resp = connection.FetchPPL(from_ip, start_date)
			iso_time = resp['time_of_ppl_generation']
			utc_time = iso_time.isoformat()
			resp['time_of_ppl_generation'] = utc_time
			return json.dumps(resp)
			return render_template('host_info.html', title="Home")
		else:
			start_date = utils.ConvertStringToISODate(start_date)
			end_date = utils.ConvertStringToISODate(end_date)
			cursor = connection.FetchPPLsRange(from_ip, start_date, end_date)
			response = []
			for i in range(cursor.count()):
				current = cursor[i]
				iso_time = current['time_of_ppl_generation']
				utc_time = iso_time.isoformat()
				current['time_of_ppl_generation'] = utc_time
				response.append(current)
			return json.dumps(response)
			return render_template('host_info.html', title="Home")
	except:
		return """<center>
			<h1 style="margin-top:100px;">Landed on a WRONG page. You must have left some field empty or entered incorrect value.<br> <a href='/'>HOME</a></h1>
			</center>
			"""

def main():
	print "Thread started"
	global connection

	public_key, private_key = utils.Get_RSA_key("LEA")

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
		iso_time = current['time_of_ppl_generation']
		utc_time = iso_time.isoformat()
		current['time_of_ppl_generation'] = utc_time
		response.append(current)
	#print "Response : ", response
	print "Size of json_data : ", len(response)
	js = json.dumps(response)
	print js
	socketio.emit('channel_logs_resp', js)

if __name__ == "__main__":

	thread = Thread(target=main)
	thread.start()

	socketio.run(app, '', port=3000, debug=True)
