"""
Process images and generate fuzzy fingerprints.

compact:
python image_manipulation.py -f extract -i ../data/icon_list_official -o something

compare:
python image_manipulation.py -i ../data/icon_list_official -b ../data/icon_list_unofficial -f compare -o somefile

"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import numpy as np
import cv2
import sys, getopt, math
# import simhash
from threading import Thread
from scipy import misc
from image_feature_extractor import FeatureExtractor, ImageMatcher

import proto.image_features_pb2 as ifp

def crop_img(img_name, x_size, y_size):
	img_data = misc.imread(img_name)
	type(img_data)
	# img = cv2.imread(img_name, 0)
	# cv2.IMREAD_COLOR
	# cv2.IMREAD_GRAYSCALE
	# cv2.IMREAD_UNCHANGED
	# img = cv2.imread(img_name, cv2.IMREAD_COLOR)
	# img = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
	img = cv2.imread(img_name, cv2.IMREAD_UNCHANGED)

	cv2.imshow(img_name, img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

def extract_feature(image_list, outfile):
	config = ifp.FeatureExtractorConfig()
	config.harris_corner = False
	config.shitomasi_corner = False
	config.sift = False
	config.surf = False
	config.fast = False
	config.brief = False
	config.orb = True 
	config.ocr = False
	extractor = FeatureExtractor(config)

	for filename in image_list:
		extractor.extract(filename)

def near_neighbor(A_list, B_list, outfile):
	config = ifp.FeatureExtractorConfig()
	extractor_A = FeatureExtractor(config)
	extractor_B = FeatureExtractor(config)
	for filename in A_list:
		extractor_A.extract(filename)
	for filename in B_list:
		extractor_B.extract(filename)
	matcher = ImageMatcher()
	res = matcher.patch_find_match(extractor_A.image_feature_dict,
			extractor_B.image_feature_dict)

def main(argv):
	has_function = False
	help_msg = "image_manipulation.py -f <function> [-x <x slice no.> -y " \
			"<y slice no.> -i <infile>], crop " \
			"[-i <image list> -o <outfile>], extract " \
			"[-i <image list A> -b <image list B> " \
			"-o <outfile>], compare"
	try:
		opts, args = getopt.getopt(argv, "hf:x:y:i:o:b:", ["function=", 
			"infile=", "outfile=", "bfile="])
	except getopt.GetoptError:
		print(help_msg)
		sys.exit(2)
	for opt, arg in opts:
		if opt == "-h":
			print(help_msg)
			sys.exit()
		elif opt in ("-f", "--function"):
			function = arg
			has_function = True
		elif opt in ("-x"):
			x_size = int(arg)
		elif opt in ("-y"):
			y_size = int(arg)
		elif opt in ("-i", "--infile"):
			infile = arg
		elif opt in ("-o", "--outfile"):
			outfile = arg
		elif opt in ("-b", "--bfile"):
			bfile = arg
		else:
			print(help_msg)
			sys.exit(2)
	if not has_function:
		print(help_msg)
		sys.exit()
	if function == "crop":
		crop_img(infile, x_size, y_size)
	elif function == "extract":
		image_list = filter(bool, open(infile, 'r').read().split('\n'))
		extract_feature(image_list, outfile)
	elif function == "compare":
		A_list = filter(bool, open(infile, 'r').read().split('\n'))
		B_list = filter(bool, open(bfile, 'r').read().split('\n'))
		near_neighbor(A_list, B_list, outfile)
	else:
		print(help_msg)
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])

