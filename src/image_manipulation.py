import numpy as np
import sys, getopt, math
import simhash
from threading import Thread
from scipy import misc

def crop_img(img_name, x_size, y_size):
	img_data = misc.imread(img_name)
	type(img_data)

def main(argv):
	has_function = False
	help_msg = "image_manipulation.py -f <function> [-x <x slice no.> -y " \
			"<y slice no.> -i <infile>"
	try:
		opts, args = getopt.getopt(argv, "hf:x:y:i:", ["function=", 
			"ifile="])
	except getopt.GetoptError:
		print help_msg
		sys.exit(2)
	for opt, arg in opts:
		if opt == "-h":
			print help_msg
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
		else:
			print help_msg
			sys.exit(2)
	if not has_function:
		print help_msg
		sys.exit()
	if function == "crop":
		crop_img(infile, x_size, y_size)
	else:
		print help_msg
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])

