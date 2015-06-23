import hashlib
import os
import proto.apk_analysis_pb2 as evalpb

def get_hexdigest(infile, func = "sha256"):
	m = getattr(hashlib, func)()
	m.update(open(infile, 'r').read())
	return m.hexdigest()

def write_proto_to_file(proto, filename):
	f = open(filename, "wb")
	f.write(proto.SerializeToString())
	f.close()

def read_proto_from_file(proto, filename):
	f = open(filename, "rb")
	proto.ParseFromString(f.read())
	f.close()

def read_proto_from_files(proto, field, filenames):
	"""For repeated proto only"""

def write_proto_to_files(proto, field, filenames):
	"""For repeated proto only"""

class GlobalFileEntryDict:
	def __init__(self):
		self.GLOBAL_FILE_ENTRY = "../../data/sdk_lib/global_file_entry.dat"
		global_file_entry = evalpb.APKDatabase()
		"""
		If file already exists, just reload it.
		Else ignore and create new one on save.
		"""
		if os.path.exists(self.GLOBAL_FILE_ENTRY):
			read_proto_from_file(global_file_entry, self.GLOBAL_FILE_ENTRY)
		self.global_file_entry_dict = dict()
		for entry in global_file_entry.record:
			self.global_file_entry_dict[entry.digest] = entry
	
	def contains(self, digest):
		return digest in self.global_file_entry_dict

	def get(self, digest):
		return self.global_file_entry_dict[digest]

	def update(self, digest, record):
		self.global_file_entry_dict[digest] = evalpb.APKRecord()
		self.global_file_entry_dict[digest].CopyFrom(record)
	
	def save(self):
		global_file_entry = evalpb.APKDatabase()
		global_file_entry.total = len(self.global_file_entry_dict)
		for digest in self.global_file_entry_dict:
			record = global_file_entry.record.add()
			record.CopyFrom(self.global_file_entry_dict[digest])
		write_proto_to_file(global_file_entry, self.GLOBAL_FILE_ENTRY)

