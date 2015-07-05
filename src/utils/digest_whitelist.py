"""
This file reads in all the hashdeep results and find the popular digests for
whitelisting purpose.
"""
import sys
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
		for entry in global_file_entry_dict.entry:
			self.digest_whitelist_dict[entry.digest] = entry

	def generate(self, apk_database):
		assert(isinstance(apk_database, evalpb.APKDatabase))
		for record in apk_database.record:
			asset_digest_file = record.asset_digest_filename
			self.update(asset_digest_file)
	
	def update(self, asset_digest_file=None, apk_record=None):
		if asset_digest_file:
			digest_dict = get_digest_dict(asset_digest_file)
		elif apk_record:
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
	
	def save(self):
		digest_whitelist = evalpb.DigestCounter()
		for digest in self.digest_whitelist_dict:
			entry = digest_whitelist.entry.add()
			entry.CopyFrom(self.digest_whitelist_dict[digest])
		write_proto_to_file(digest_whitelist, self.DIGEST_WHITELIST)

def main(args):
	None

if __name__ == "__main__":
	main(sys.argv[1:])

