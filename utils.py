from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA
from bitarray import bitarray
from bson.binary import Binary
from json import dumps
from math import ceil, log

import ast, unicodedata

import dbhelper


import datetime
import random
import hashlib
import base64
import os

DEBUG_LEVEL = 10

connection = dbhelper.MConnection(debug=DEBUG_LEVEL)

class BloomFilter(object):
	def __init__(self, capacity=500000, bloom_dict=None, error_rate=0.01, ip=None):
		self.capacity = capacity
		self.error_rate = error_rate
		self.hash_count = 0
		self.bits_count = 0
		self.bit_array = 0
		self.ip = None

		if bloom_dict == None:
			self.ip = ip

			#Calculate number of bits required in bloomfilter
			# bits_count = (capacity x ln(error_rate)) / (ln2)^2
			self.bits_count = int(ceil(abs((self.capacity * log(self.error_rate)) / log(2)**2)))
			self.bitarray = bitarray(self.bits_count)
	
			#Hash itererations needed
			# hash_count = log2 * (bits_count/capacity)
			self.hash_count = int(ceil((self.bits_count/self.capacity) * log(2)))
	
			printMessage(3, "Item Capacity: %d, Error Rate: %f, Bits Count: %d, Hash Count: %d"%(self.capacity, self.error_rate, self.bits_count, self.hash_count))

			self.bit_array = bitarray(self.bits_count)
			self.bit_array.setall(0)
			printMessage(3, "Created a fresh bitarray")



		#If bitarray is created from existing bitarray from mongodb database
		else:
			self.ip = str(bloom_dict['ip'])
			self.capacity = int(bloom_dict['capacity'])
			self.error_rate = float(bloom_dict['error_rate'])
			self.hash_count = int(bloom_dict['hash_count'])
			self.bits_count = int(bloom_dict['bits_count'])
			self.bit_array = bitarray()
			data = bloom_dict['accumulator']
			for i in range(len(data)):
				letter  = data[i]
				if letter == '1':
					self.bit_array.append(1)
				else:
					self.bit_array.append(0)

			printMessage(3, "Creating a bitarray from database")


	def AddToFilter(self, data):
		for seed in xrange(self.hash_count):
			result = int(hashlib.sha256(str(seed) + data).hexdigest(), base=16) % self.bits_count
			self.bit_array[result] = 1

	def Lookup(self, data):
		for seed in xrange(self.hash_count):
			result = int(hashlib.sha256(str(seed) + data).hexdigest(), base=16) % self.bits_count
			if self.bit_array[result] == 0:
				return 0
		return 1

	def Serialise(self):
		printMessage(8, "Serialising Bloomfilter object")
		bloom_dict = {}
		bloom_dict['ip'] = self.ip
		bloom_dict['capacity'] = self.capacity;
		bloom_dict['error_rate'] = self.error_rate
		bloom_dict['hash_count'] = self.hash_count
		bloom_dict['bits_count'] = self.bits_count
		str_accumulator = ""
		for i in range(len(self.bit_array)):
			bit = self.bit_array[i]
			if bit == True:
				str_accumulator += "1"
			else:
				str_accumulator += "0"
		bloom_dict['accumulator'] = str_accumulator
		return bloom_dict

def bloom_filter_lookup(bf, word):
	start = datetime.datetime.now().isoformat()
	res = bf.Lookup(word)
	end = datetime.datetime.now()
	return (res, (end-start).microseconds)

def array_lookup(array, word):
	start = datetime.datetime.now()
	res = 0
	for w in array:
		if w == word:
			res = 1
			break
	end = datetime.datetime.now()
	return (res, (end-start).microseconds)

def CreateNewBloomFilter():
	filter = BloomFilter(capacity=200, error_rate=10)
	return filter.Serialise()


def TestBloomFilter():
	filter = BloomFilter(capacity=200, error_rate=10)
	lines = open('keys/words.txt', 'r')
	array = []
	i = 0
	for line in lines:
		if i > 50:
			break
		i += 1;
		array.append(line)
		filter.AddToFilter(line)
	lines.close()
	word_count = len(array)

	return filter.Serialise()
	

	for i in range(word_count):
		word = array[random.randrange(0, word_count)]
		print word.strip(), " BloomFilter : ", bloom_filter_lookup(filter, word)
		print word.strip(), " ArrayLookup : ", array_lookup(array, word)
		print "\n\n"


def printMessage(debug, message):
	global DEBUG_LEVEL
	if debug <= DEBUG_LEVEL:
		print "\n[",debug,"]",message, "\n\n"

def generate_RSA_keys(bits=2048):
	new_key = RSA.generate(bits, e=65537)
	#public_key = new_key.publickey()
	private_key = new_key
	return private_key

def save_key(key, name):
	pwd = os.getcwd()
	dir_key = os.path.join(pwd, 'keys')

	private = key.exportKey("PEM")
	public = key.publickey().exportKey("PEM")

	with open(os.path.join(dir_key, name + "PrivateKey.pem"), 'wb') as f:
		f.write(private)

	with open(os.path.join(dir_key, name + "PublicKey.pem"), 'wb') as f:
		f.write(public)

def get_hash(data):
	hashed = str(hashlib.sha1(data).hexdigest())
	return hashed

def Get_RSA_key(agency_name, ktype):
	key = get_rsa_key(agency_name, ktype=ktype)
	#public = key.publickey()
	#private = key
	return key

def EncryptData(dict_data, encrypting_key, dict_keys=None):
	printMessage(10, "Encrypting with key : " + encrypting_key.exportKey("PEM"))
	data = ""
	if dict_keys == None:
		for index, val in dict_data.iteritems():
			data += str(index)+ "=" + str(val) + ","
	else:
		for index in dict_keys:
			data += str(index) + "=" + str(dict_data[index]) + ","
	data = data[:-1]

	return encrypt_data(data, encrypting_key)

def encrypt_data(str_data, encrypting_key):
	encrypted_raw, = encrypting_key.encrypt(str_data, 1024)
	encrypted = base64.b64encode(encrypted_raw)
	return encrypted

def DecryptData(str_data, decrypting_key):
	decrypted = decrypt_data(str_data, decrypting_key)
	arr_key_val = decrypted.split(',')
	dict_data = {}
	for pair in arr_key_val:
		key, val = pair.split('=')
		dict_data[key] = val
	return dict_data

def decrypt_data(str_data, decrypting_key):
	printMessage(10, "Decrypting with key : " + decrypting_key.exportKey("PEM"))
	encrypted_raw = base64.b64decode(str_data)
	return decrypting_key.decrypt(encrypted_raw)

def CreateLogChain(encrypted_log_entry, prev_log_chain):
	data_to_hash = str(encrypted_log_entry) + str(prev_log_chain)
	current_log_chain = get_hash(data_to_hash)
	return current_log_chain

def SequenceVerification(prev_dble, current_dble):
	data_to_hash = str(current_dble['encrypted_log']) + str(prev_dble['hash'])
	current_log_chain = get_hash(data_to_hash)
	return (current_log_chain == current_dble['hash'])

def generate_signature(private_key, data):
	h = SHA.new()
	h.update(data)

	signer = PKCS1_PSS.new(private_key)
	signature = signer.sign(h)

	#hashed = get_hash(data)
	#hashed = base64.b64encode(hashed)
	#temp_data = str(private_key.sign(data, '')[0])
	
	signature_dict = {}
	temp_data = base64.b64encode(signature)
	signature_dict['actual_data'] = data
	signature_dict['signature'] = temp_data
	return signature_dict


def GeneratePPL():
	global connection
	accumulators_cursor = connection.get_all_todays_accumulators()

	for i in range(accumulators_cursor.count()):
		accumulator = accumulators_cursor[i]
		accumulator = ast.literal_eval(dumps(accumulator))
		print(1, accumulator)
		time_of_ppl_generation = datetime.datetime.now()
		data = ""
		data += "accumulator=" + accumulator['accumulator'] + ",time=" + time_of_ppl_generation.isoformat()
		private_key = Get_RSA_key("CSP", "private")
		ppl_dict = generate_signature(private_key, data)
		ppl_dict['time_of_ppl_generation'] = time_of_ppl_generation
		ppl_dict['ip'] = accumulator['ip']
		connection.SavePPL(ppl_dict)
		print "Inseted PPL"

def get_key_path(agency_name, ktype):
	pwd = os.getcwd()
	dir_key = os.path.join(pwd, 'keys')

	apath = None

	if agency_name == "LEA":
		if ktype == "private":
			apath  = os.path.join(dir_key, "LawEnforcementAgencyPrivateKey.pem")
		else:
			apath = os.path.join(dir_key, "LawEnforcementAgencyPublicKey.pem")
	else:
		if ktype == "private":
			apath = os.path.join(dir_key, "CloudServiceProviderPrivateKey.pem")
		else:
			apath = os.path.join(dir_key, "CloudServiceProviderPublicKey.pem")
	return apath

def get_rsa_key(agency_name, ktype=None):
	pwd = os.getcwd()
	dir_key = os.path.join(pwd, 'keys')
	lea_public_key = get_key_path("LEA", "public")
	lea_private_key = get_key_path("LEA", "private")
	csp_public_key = get_key_path("CSP", "public")
	csp_private_key = get_key_path("CSP", "private")

	if agency_name == "LEA":
		if os.path.isfile(lea_public_key) and os.path.isfile(lea_private_key):
		#and os.path.isfile(csp_private_key) and os.path.isfile(csp_public_key):
			printMessage(3, "Reading RSA key from file")
			if ktype == "private":
				rsa_key = RSA.importKey(open(lea_private_key, "rb").read())
			else:
				rsa_key = RSA.importKey(open(lea_public_key, "rb").read())
			return rsa_key
		else:
			printMessage(3, "Generating new RSA key")
			rsa_key = generate_RSA_keys()
			save_key(rsa_key, "LawEnforcementAgency")
			return rsa_key
	else:
		if os.path.isfile(csp_private_key) and os.path.isfile(csp_public_key):
			printMessage(3, "Reading RSA key from file")
			if ktype == "private":
				rsa_key = RSA.importKey(open(csp_private_key, "rb").read())
			else:
				rsa_key = RSA.importKey(open(csp_public_key, "rb").read())
			return rsa_key
		else:
			printMessage(3, "Generating new RSA key")
			rsa_key = generate_RSA_keys()
			save_key(rsa_key, "CloudServiceProvider")
			return rsa_key

def VerifySignature(public_key_str, actual_data, signature):
	public_key= Get_RSA_key("CSP", "public")
	#signature = unicodedata.normalize('NFKD', signature).encode('ascii','ignore')
	signature = signature.strip()
	signature = base64.b64decode(signature)

	h = SHA.new()
	h.update(actual_data)

	verifier = PKCS1_PSS.new(public_key)
	res = verifier.verify(h, signature)

	#res = public_key.verify(actual_data, signature)

	if res:
		print "Authenticity Verification PASSED"
		return True
	else:
		print "Authenticity Verification FAILED"
		return False

def ConvertStringToISODate(date_str):
	return datetime.datetime.strptime( date_str, "%Y-%m-%dT%H:%M:%S.%f" )

# Just a helper function to test the current module
def bloomNDatabaseConnection():
	bloom_dict = TestBloomFilter()

	ip = "192.168.1.4"

	bloom_dict['ip'] = ip

	global connection

	current = connection.get_current_accumulator(ip)

	if current == None:
		connection.update_accumulator(bloom_dict)

	else:
		BloomFilter(bloom_dict=current)


if __name__ == "__main__":
	#TestBloomFilter()

	bloomNDatabaseConnection()
