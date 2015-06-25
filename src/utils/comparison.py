"""
Unzip and compute hash values for an app. Compute similarities between apps.

unzip and compute hash values, then remove directory:
python comparison.py -f digest -i apk_file -o digest_file

compute similarity between one digest file against a list of digest files,
output result for each pair:
python comparison.py -f compare -i digest_file -c compare_against -o compare_results

compare the gpl list and non-gpl list of apks to find violations.
python comparison.py -f find_violation -i gpl_list -c non_gpl_list -o outfile

# Test the commands
python comparison.py -f compare -i
../../data/sdk_lib/GPL_libs/ffmpeg-android-master.zip -c
../../data/sdk_lib/F-droid-apps/gpl_download/compare_list -o temp

"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import logging
import os
import sys, getopt, math
import subprocess
import commands
import re
from time import gmtime, strftime
import proto.apk_analysis_pb2 as evalpb

from util import (get_hexdigest, write_proto_to_file, read_proto_from_file, 
		GlobalFileEntryDict, unpack, remove, find_text_in_dir, digest,
		digest_batch)
from util import GPL_STRING, HASHDEEP_SUFFIX 

def find_violation(gpl_list, non_gpl_list, outfile):
	"""Compare similarit betwen files in gpl_list and non_gpl_list. 
	If there is high similarity, then it is violation"""
	gpl_file_list = filter(bool, open(gpl_list, 'r').read().split('\n'))
	evaluation = evalpb.EvaluationPB()
	evaluation.timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	for gpl_file in gpl_file_list:
		eval_result = evaluation.result.add()
		result = compare(infile = gpl_file, compare_list = non_gpl_list,
				similarity_bar = 1)
		logger = logging.getLogger("global")
		logger.info("Inside find violation")
		logger.info("gpl file is: %s" % gpl_file)
		logger.info(result)
		eval_result.CopyFrom(result)
	write_proto_to_file(evaluation, outfile)

def _get_digest_set(filename):
	"""get the sha256 digest set from hashdeep output.
	"""
	digest_list = filter(bool, open(filename, 'r').read().split('\n'))
	digest_list = [digest.split(',')[2] for digest in digest_list 
			if (digest[0] not in "%#")]
	digest_set = set(digest_list)
	return digest_set

def compare(infile, compare_list, outfile=None, similarity_bar=0):
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
			result.current.gpl_matches.smali_filename.extend(gpl_files)
		remove(infile)
	in_set = _get_digest_set(result.current.asset_digest_filename)
	if not apk_records_dict.contains(in_digest):
		result.current.asset_count = len(in_set)
		apk_records_dict.update(in_digest, result.current)

	# Set info for comparison files.
	compare_digest_files = filter(bool, open(compare_list, 'r').read().split('\n'))
	for compare_digest_file in compare_digest_files:
		file_entry = evalpb.CompareFileEntry()
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
				file_entry.comparison.gpl_matches.smali_filename.extend(gpl_files)
			remove(compare_digest_file)
		compare_set = _get_digest_set(file_entry.comparison.asset_digest_filename)
		if not apk_records_dict.contains(comp_digest):
			file_entry.comparison.asset_count = len(compare_set)
			apk_records_dict.update(comp_digest,
					file_entry.comparison)
		file_entry.common_count = len(in_set & compare_set)
		file_entry.common_ratio = (float(file_entry.common_count) / 
				max(len(in_set), len(compare_set)))
		# common count or common ratio ?
		if file_entry.common_count > similarity_bar:
			result_file_entry = result.file_entry.add()
			result_file_entry.CopyFrom(file_entry)

	# Write the results to file.
	apk_records_dict.save()
	print result
	if outfile:
		write_proto_to_file(result, outfile)
	return result

def main(argv):
	logging.basicConfig(format='%(asctime)s - %(name)s - '
			'%(levelname)s : %(message)s',
			datefmt='%m/%d/%Y %I:%M:%S %p',
			filename='./log', level=logging.DEBUG)

	help_msg = ("comparison.py -f <function> [-i <apk_file> -o <digest_file> -b], "
			"digest [-i <digest_file> -c <compare_list> -o " 
			"<outfile>], compare, [-i <gpl_list> -c <non_gpl_list> -o <outfile>], "
			"find_violation")
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
	elif function == "find_violation":
		gpl_list = infile
		non_gpl_list = compare_list
		find_violation(gpl_list, non_gpl_list, outfile)
	else:
		print(help_msg)
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])

