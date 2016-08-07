from pymongo import MongoClient
from datetime import datetime
import utils
import pymongo
pymongo.unicode_decode_output = True

class MConnection():
	def __init__(self, debug=0):
		self.database_server_add = "localhost"
		self.database_server_port = 27017

		self.database_name = "freelancer"
		self.collection_name = "logs_storage"
		self.collection_name_accumulator = "proof_storage"
		self.collection_name_PPL = "ppl_storage"

		self.debug = debug
		self.connection = MongoClient(self.database_server_add, self.database_server_port)
		self.local_db = self.connection[self.database_name]
		self.collection = self.local_db[self.collection_name]
		self.collection_accumulator = self.local_db[self.collection_name_accumulator]
		self.collection_PPL = self.local_db[self.collection_name_PPL]

	def DropLogsCollection(self):
		self.collection.drop()
		self.collection_accumulator.drop()

	def DropPPLsCollection(self):
		self.collection_PPL.drop()

	def DropAll(self):
		self.DropLogsCollection()
		self.DropPPLsCollection()

	def fetch_all(self, limit=20):

		local_collection = self.collection

		cursor = local_collection.find({},{'_id':0})  #.limit(limit);

		return cursor

	def update_accumulator(self, accumulator_entry):
		local_collection = self.collection_accumulator
		current_date = str(datetime.now().date())
		#acc = acc.tobytes()
		data = {}
		data['time'] = current_date
		utils.printMessage(10, accumulator_entry)
		data['ip'] = accumulator_entry['ip']
		#db_accu = self.get_current_accumulator(accumulator_entry['ip'])
		#if db_accu == None:
		#	data['accumulator'] = acc
		#	print "Inserting : ", data
		#	local_collection.insert_one(data)
		#else:
		utils.printMessage(10, accumulator_entry)
		local_collection.update(data, {"$set": accumulator_entry}, upsert=True)

	def get_all_todays_accumulators(self):
		local_collection = self.collection_accumulator
		current_date = str(datetime.now().date())
		data = {}
		data['time'] = current_date
		cursor = local_collection.find(data,{'_id':0, 'time':0})
		print "Cursor is ",cursor, " length : ",cursor.count()
		if cursor.count() == 0:
			return None
		else:
			return cursor

	def FetchLogsRange(self, ip, start_date, end_date):
		local_collection = self.collection
		if ip != None:
			data_to_search = {'from_ip' : ip, 'time': {"$gte" : start_date, "$lte" : end_date} }
		else:
			data_to_search = {'time': {"$gte" : start_date, "$lte" : end_date} }
		cursor = local_collection.find(data_to_search, {'_id':0})

		return cursor


	def get_current_accumulator(self, ip):
		local_collection = self.collection_accumulator
		current_date = str(datetime.now().date())
		data = {}
		data['time'] = current_date
		data['ip'] = ip
		cursor = local_collection.find(data,{'_id':0, 'time':0})
		print "Cursor is ",cursor, " length : ",cursor.count()
		if cursor.count() == 0:
			return None
		else:
			return cursor[0]

	def get_accumulator(self, ip, time):
		local_collection = self.collection_accumulator
		data = {}
		data['time'] = time
		data['ip'] = ip
		cursor = local_collection.find(data,{'_id':0})
		print "Cursor is ",cursor, " length : ",cursor.count()
		if cursor.count() == 0:
			return None
		else:
			return cursor[0]

	def get_latest_log_chain(self):
		local_collection = self.collection
		cursor = local_collection.find(limit=1).sort('$natural',-1)

		if cursor.count() == 0:
			return ""
		return cursor[0]['hash']

	def save_log_chain(self, encrypted_log_entry, log_chain):
		data = {'hash' : log_chain, 'encrypted_log' : encrypted_log_entry['encrypted_log'], 'from_ip' : encrypted_log_entry['from_ip'],'time':encrypted_log_entry['time']}
		if self.debug > 7:
			print "[", self.debug, "]", "Data to be inserted : ", data
		try:
			local_collection = self.collection
			local_collection.insert_one(data)
			if self.debug > 5:
				print "[", self.debug, "]", "Record inserted successfully"
		except Exception, err:

			if self.debug > 1:
				print "[", self.debug, "]", "Unable to save current log_chain"
				print str(err)

	def SavePPL(self, data):
		if self.debug > 7:
			print "[", self.debug, "]", "Data to be inserted : ", data
		try:
			local_collection = self.collection_PPL
			local_collection.insert_one(data)
			if self.debug > 5:
				print "[", self.debug, "]", "Record inserted successfully"
		except Exception, err:

			if self.debug > 1:
				print "[", self.debug, "]", "Unable to save ppl"
				print str(err)

	def FetchAllPPl(self):

		local_collection = self.collection_PPL

		cursor = local_collection.find({},{'_id':0, 'time':0})  #.limit(limit);

		return cursor

	def FetchPPLsRange(self, ip, start_date, end_date):
		local_collection =self.collection_PPL

		data_to_search = {'ip' : ip, 'time_of_ppl_generation': {"$gte" : start_date, "$lte" : end_date} }

		cursor = local_collection.find(data_to_search, {'_id':0, 'time':0})

		return cursor

	def FetchPPL(self, ip, time):
		local_collection = self.collection_PPL

		data_to_search = {'ip' : ip, 'time_of_ppl_generation' : time }

		cursor = local_collection.find(data_to_search, {'_id':0, 'time':0})  #.limit(limit);

		print "Size of cursor : ", cursor.count()

		return cursor[0]

	def SaveLogEntryInDatabase(self, encrypted_log_entry):
		prev_log_chain = self.get_latest_log_chain()
		current_log_chain = utils.CreateLogChain(encrypted_log_entry['encrypted_log'], prev_log_chain)
		self.save_log_chain(encrypted_log_entry, current_log_chain)

if __name__ == "__main__":
	connection = MConnection()
	#print connection.fetch_all()

	
	connection.update_accumulator("172.10.16.233", "Kuch Bhi")

	connection.fetch_all()