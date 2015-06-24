"""
Unzip and compute hash values for an app. Compute similarities between apps.

unzip and compute hash values, then remove directory:
python comparison.py -f digest -i apk_file -o digest_file

compute similarity between one digest file against a list of digest files,
output result for each pair:
python comparison.py -f compare -i digest_file -c compare_against -o compare_results

# Test the commands
python comparison.py -f compare -i
../../data/sdk_lib/GPL_libs/ffmpeg-android-master.zip -c
../../data/sdk_lib/F-droid-apps/gpl_download/compare_list -o temp

"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import os
import sys, getopt, math
import subprocess
import commands
import re
import proto.apk_analysis_pb2 as evalpb

from util import (get_hexdigest, write_proto_to_file, read_proto_from_file, 
		GlobalFileEntryDict, unpack, remove, find_text_in_dir, digest,
		digest_batch)
from util import GPL_STRING, HASHDEEP_SUFFIX 

def _get_digest_set(filename):
	"""get the sha256 digest set from hashdeep output.
	"""
	digest_list = filter(bool, open(filename, 'r').read().split('\n'))
	digest_list = [digest.split(',')[2] for digest in digest_list 
			if (digest[0] not in "%#")]
	digest_set = set(digest_list)
	return digest_set

def compare(infile, compare_list, outfile=None):
	"""Compare digest of infile against compare_list, output to outfile

	@parameter
	infile: the digest file of candidate
	compare_list: the list of files to compare against
	outfile: the compare results, containing pairs compared and the results,
		if None, doesn't write
	@return
	result: instance of DigestComprisonResult
	"""
	apk_records_dict = GlobalFileEntryDict()

	result = evalpb.DigestComparisonResult()

	# Set info related to current file.
	# size,md5,sha256,filename
	# use sha256
	in_digest = get_hexdigest(infile)
	if apk_records_dict.contains(in_digest):
		result.current.CopyFrom(apk_records_dict.get(in_digest))
	else:
		result.current.digest = in_digest
		result.current.filename = infile
		asset_filename = infile + HASHDEEP_SUFFIX
		result.current.asset_digest_filename = asset_filename
		infile = unpack(infile)
		digest(infile, asset_filename)
		gpl_files = find_text_in_dir(infile, GPL_STRING)
		if len(gpl_files) > 0:
			result.current.matches.smali_filename.extend(gpl_files)
		remove(infile)
	in_set = _get_digest_set(result.current.asset_digest_filename)
	if not apk_records_dict.contains(in_digest):
		result.current.asset_count = len(in_set)
		apk_records_dict.update(in_digest, result.current)

	# Set info for comparison files.
	compare_digest_files = filter(bool, open(compare_list, 'r').read().split('\n'))
	for compare_digest_file in compare_digest_files:
		file_entry = result.file_entry.add()
		comp_digest = get_hexdigest(compare_digest_file)
		if apk_records_dict.contains(comp_digest):
			file_entry.comparison.CopyFrom(apk_records_dict.get(comp_digest))
		else:
			file_entry.comparison.digest = comp_digest
			file_entry.comparison.filename = compare_digest_file
			asset_filename = compare_digest_file + HASHDEEP_SUFFIX
			file_entry.comparison.asset_digest_filename = asset_filename
			compare_digest_file = unpack(compare_digest_file)
			digest(compare_digest_file, asset_filename)
			gpl_files = find_text_in_dir(compare_digest_file, GPL_STRING)
			if len(gpl_files) > 0:
				file_entry.comparison.matches.smali_filename.extend(gpl_files)
			remove(compare_digest_file)
		compare_set = _get_digest_set(file_entry.comparison.asset_digest_filename)
		if not apk_records_dict.contains(comp_digest):
			file_entry.comparison.asset_count = len(compare_set)
			apk_records_dict.update(comp_digest,
					file_entry.comparison)
		file_entry.common_count = len(in_set & compare_set)
		file_entry.common_ratio = (float(file_entry.common_count) / 
				max(len(in_set), len(compare_set)))

	# Write the results to file.
	apk_records_dict.save()
	print result
	if outfile:
		write_proto_to_file(result, outfile)
	return result

def main(argv):
	help_msg = ("comparison.py -f <function> [-i <apk_file> -o <digest_file> -b], "
			"digest [-i <digest_file> -c <compare_list> -o " 
			"<outfile>], compare")
	try:
		opts, args = getopt.getopt(argv, "hf:i:o:c:b", ["function=", 
			"infile=", "outfile=", "compare_list="])
	except getopt.GetoptError:
		print(help_msg)
		sys.exit(2)
	has_function = False
	batch = False
	outfile = None
	for opt, arg in opts:
		if opt == "-h":
			print(help_msg)
			sys.exit()
		elif opt in ("-f", "--function"):
			function = arg
			has_function = True
		elif opt in ("-b"):
			batch = True
		elif opt in ("-c"):
			compare_list = arg
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
	if function == "digest":
		if batch:
			digest_batch(infile, outfile)
		else:
			infile = unpack(infile)
			digest(infile, outfile)
			remove(infile)
	elif function == "compare":
		compare(infile, compare_list, outfile)
	else:
		print(help_msg)
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])

