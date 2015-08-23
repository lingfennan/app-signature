import hashlib
import os
import subprocess
import proto.apk_analysis_pb2 as evalpb

from util_constants import GPL_STRING, LICENCE_FILENAME, HASHDEEP_SUFFIX

"""
Utilities for app processing
"""
def get_file_type(filename):
	if filename.endswith('.smali'):
		return evalpb.DigestEntry.SMALI
	elif filename.lower().endswith(('.png', '.jpg', '.bmp', '.jpeg', '.gif',
		'.tif')):
		return evalpb.DigestEntry.IMAGE
	elif filename.lower().endswith('.xml'):
		return evalpb.DigestEntry.XML
		# Tuple
	elif filename.lower().endswith(('.mp4', '.flv', '.mkv', '.avi', '.wmv',
			'.rm', '.rmvb', '.mpeg', '.mpg', '.m4v', '.ogg')):
		return evalpb.DigestEntry.VIDEO
	else:
		return evalpb.DigestEntry.UNKNOWN

def get_digest_dict(filename):
	"""get the sha256 digest and filename mapping from hashdeep output.
	"""
	digest_list = filter(bool, open(filename, 'r').read().split('\n'))
	digest_dict = dict()
	for digest_line in digest_list:
		if digest_line[0] not in "%#":
			_, _, digest, filepath = digest_line.split(',')
			digest_dict[digest] = filepath.split('app-signature')[1]
	return digest_dict

def unpack(infile):
	""" unpack the file 
	@parameter
	infile: zip or apk file
	@return
	unpack: the output directory
	"""
	apk_suffix = ".apk"
	zip_suffix = ".zip"
	if infile.endswith(apk_suffix):
		unpack = infile[:-4]
		p1 = subprocess.Popen(["apktool", "d", infile, "-o", unpack],
				stdout=subprocess.PIPE)
		output, error = p1.communicate()
	elif infile.endswith(zip_suffix):
		unpack = infile[:-4]
		p1 = subprocess.Popen(["unzip", infile, "-d", unpack],
				stdout=subprocess.PIPE)
		output, error = p1.communicate()
	else:
		raise Exception("Unhandled file extension")
	return unpack

def digest(infile, outfile=None):
	"""
	hashdeep -r dir, pipe to a file
	@parameter
	infile: the input file or directory name
	outfile: output file name
	@return
	True if success otherwise False
	"""
	# If outfile is not specified
	if not outfile:
		outfile = infile + HASHDEEP_SUFFIX
	# The input of hashdeep need to be absolute path, otherwise, there will
	# be bug.
	infile = os.path.abspath(infile)
	p = subprocess.Popen(['hashdeep', '-r', infile], stdout=subprocess.PIPE)
	output, error = p.communicate()
	open(outfile, 'w').write(output)
	return False if error else True

def remove(indir):
	""" Remove the decompressed files """
	p = subprocess.Popen(['rm', '-r', indir], stdout=subprocess.PIPE)
	output, error = p.communicate()
	return False if error else True

def find_text_in_dir(indir, text, ignore_binary=True, ignore_case=False):
	"""
	Find files containing text in directory using grep.
	:param indir: the directory to search in.
	:param text: regular expression to match.
	:param ignore_binary: ignore binary files.
	:param ignore_case: case-insensitivity.
	:return: list of string, split output of grep.
	"""
	flags = '-rlI' if ignore_binary else '-rl'
	p = subprocess.Popen(['grep', flags, text, indir],
			stdout=subprocess.PIPE)
	output, error = p.communicate()
	return filter(bool, output.split("\n"))

def find_file_in_dir(indir, filename, ignore_case=True):
	"""Find file containing filename in directory using find."""
	# Do we really need this now?
	flags = '-iname' if ignore_case else '-name'
	p = subprocess.Popen(['find', indir, flags, filename],
						 stdout=subprocess.PIPE)
	output, error = p.communicate()
	return filter(bool, output.split("\n"))

def get_hexdigest(infile, func = "sha256"):
	m = getattr(hashlib, func)()
	m.update(open(infile, 'r').read())
	return m.hexdigest()

def digest_batch(infile, outdir=None):
	infile_list = filter(bool, open(infile, 'r').read().split('\n'))
	for infile in infile_list:
		outfile = (outdir + infile.split("/")[-1] + HASHDEEP_SUFFIX if
				outdir else None)
		infile = unpack(infile)
		digest(infile, outfile)
		remove(infile)

"""
Utilities for protocol buffer
"""
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

"""
Utilities for logging 
"""
class GlobalFileEntryDict:
	def __init__(self):
		self.GLOBAL_FILE_ENTRY = "../../data/global_app_entry.dat"
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

