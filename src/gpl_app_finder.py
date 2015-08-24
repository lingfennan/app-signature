__author__ = 'ruian'

# 1. Try all the hashdeep files first. Find how many of them has license.txt.
# 2. Find GPL string in all the files and list them.
# 3. Compare the GPL applications against the other GPL applications.

import logging
import os
import sys, getopt, math

import subprocess
import commands
import re
from time import gmtime, strftime
from multiprocessing import Pool
from utils.util_constants import HASHDEEP_SUFFIX, GPL_STRING

import utils.proto.apk_analysis_pb2 as evalpb
from utils.util import (get_hexdigest, get_file_type, write_proto_to_file, read_proto_from_file,
                        GlobalFileEntryDict, unpack, remove, find_text_in_dir, digest,
                        digest_batch, get_digest_dict)
from utils.comparison import get_digest_set

play_app_dict = GlobalFileEntryDict('../data/flexdroid/play_gpl_apps')

def find_gpl(apk_file):
    in_digest = get_hexdigest(apk_file)
    if play_app_dict.contains(in_digest):
        # Already computed
        return
    record = evalpb.APKRecord()
    record.digest = in_digest
    record.filename = apk_file
    record.asset_digest_filename = apk_file + HASHDEEP_SUFFIX
    record.file_size = os.path.getsize(apk_file)
    indir = unpack(apk_file)
    digest(indir, record.asset_digest_filename)
    gpl_files = find_text_in_dir(indir, GPL_STRING)
    if len(gpl_files) > 0:
        smali_filenames = []
        asset_filenames = []
        for f in gpl_files:
            smali_filenames.append(f) if get_file_type(f) == evalpb.DigestEntry.SMALI else asset_filenames.append(f)
        record.gpl_matches.smali_filename.extend(smali_filenames)
        record.gpl_matches.asset_filename.extend(asset_filenames)
    remove(indir)
    compare_set = get_digest_set(record.asset_digest_filename)
    if not play_app_dict.contains(in_digest):
        record.asset_count = len(compare_set)
        play_app_dict.update(in_digest, record)
        play_app_dict.save()

def find_gpl_parallel(inlist, poolsize=8):
    pool = Pool(processes=poolsize)
    pool.map(find_gpl, inlist)

def main(argv):
    logging.basicConfig(format='%(asctime)s - %(name)s - '
                               '%(levelname)s : %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename='./log', level=logging.DEBUG)

    help_msg = ("gpl_app_finder.py -f <function> [-i <apk_file> -o <digest_file>], find_gpl")
    try:
        opts, args = getopt.getopt(argv, "hf:i:o:", ["function=", "infile=", "outfile="])
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
    if function == "find_gpl":
        inlist = filter(bool, open(infile, 'r').read().split('\n'))
        find_gpl_parallel(inlist)
    else:
        print(help_msg)
        sys.exit()
