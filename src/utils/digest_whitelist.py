"""
This file reads in all the hashdeep results and find the popular digests for
whitelisting purpose.


python digest_whitelist.py -f generate_whitelist -i
../../data/global_app_entry.dat
"""
import logging
import sys, getopt, os
from util import (read_proto_from_file, write_proto_to_file, get_file_type, 
		get_digest_dict)
import proto.apk_analysis_pb2 as evalpb

class DigestWhitelist:
	def __init__(self):
		self.DIGEST_WHITELIST = "./digest_whitelist"
		digest_whitelist = evalpb.DigestCounter()
		if os.path.exists(self.DIGEST_WHITELIST):
			read_proto_from_file(digest_whitelist, self.DIGEST_WHITELIST)
		self.digest_whitelist_dict = dict()
		for entry in digest_whitelist.entry:
			self.digest_whitelist_dict[entry.digest] = entry

	def generate(self, apk_database):
		assert(isinstance(apk_database, evalpb.APKDatabase))
		for record in apk_database.record:
			asset_digest_file = record.asset_digest_filename
			self.update(asset_digest_file)
	
	def update(self, asset_digest_file=None, apk_record=None):
		if asset_digest_file:
			assert(isinstance(asset_digest_file, unicode))
			digest_dict = get_digest_dict(asset_digest_file)
		elif apk_record:
			assert(isinstance(apk_record, evalpb.APKRecord))
			digest_dict = get_digest_dict(apk_record.asset_digest_filename)
		else:
			raise Exception("Either asset_digest_file or apk_record "
					"should be not None")
		for digest in digest_dict:
			if digest in self.digest_whitelist_dict:
				self.digest_whitelist_dict[digest].count += 1
			else:
				entry = evalpb.DigestEntry()
				entry.digest = digest
				entry.count = 1
				entry.sample_filename = digest_dict[digest]
				entry.file_type = get_file_type(
						digest_dict[digest])
				self.digest_whitelist_dict[digest] = evalpb.DigestEntry()
				self.digest_whitelist_dict[digest].CopyFrom(entry)
	
	def get_digests(self, threshold = 10):
		"""Return the whitelist given threshold.
		"""
		return [digest for digest in self.digest_whitelist_dict if 
				self.digest_whitelist_dict[digest].count >= 
				threshold]
	
	def get_entry(self, digest):
		return self.digest_whitelist_dict[digest]

	def size(self):
		return len(self.digest_whitelist_dict)
	
	def save(self):
		digest_whitelist = evalpb.DigestCounter()
		for digest in self.digest_whitelist_dict:
			entry = digest_whitelist.entry.add()
			entry.CopyFrom(self.digest_whitelist_dict[digest])
		write_proto_to_file(digest_whitelist, self.DIGEST_WHITELIST)


def generate_whitelist(apk_database_fname):
	dw = DigestWhitelist()
	apk_database = evalpb.APKDatabase()
	read_proto_from_file(apk_database, apk_database_fname)
	logging.info("Number of apkrecords:", len(apk_database.record))
	dw.generate(apk_database)
	logging.info("Number of whitelist items:", dw.size())
	logging.info("Number of whitelist threshold 0:",
			len(dw.get_digests(self, threshold = 0)))
	logging.info("Number of whitelist threshold 2:",
			len(dw.get_digests(self, threshold = 1)))
	dw.save()

def main(argv):
	logging.basicConfig(format='%(asctime)s - %(name)s - '
			'%(levelname)s : %(message)s',
			datefmt='%m/%d/%Y %I:%M:%S %p',
			filename='./log', level=logging.DEBUG)

	help_msg = ("digest_whitelist.py -f <function> [-i infile] generate_whitelist")
	try:
		opts, args = getopt.getopt(argv, "hf:i:o:", ["function=", 
			"infile=", "outfile="])
	except getopt.GetoptError:
		print(help_msg)
		sys.exit(2)
	has_function = False
	outfile = None
	for opt, arg in opts:
		if opt == "-h":
			print(help_msg)
			sys.exit()
		elif opt in ("-f", "--function"):
			function = arg
			has_function = True
		elif opt in ("-i", "--infile"):
			infile = arg
		elif opt in ("-o", "--outfile"):
			outfile = arg
		else:
			print(help_msg)
			sys.exit(2)
	if not has_function:
		print(help_msg)
		sys.exit()
	if function == "generate_whitelist":
		generate_whitelist(infile)

if __name__ == "__main__":
	main(sys.argv[1:])

