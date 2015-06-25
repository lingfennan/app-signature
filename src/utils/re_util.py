"""
Do regular expression matches.

get gpl applications:
python re_util.py -f gpl -o outfile

download sdk and source tarball:
python re_util.py -f download -i gpl_list -o outfile
"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import sys, getopt, math
import urllib2
from urllib import urlretrieve as retrieve 
import re

def download_url(url):
	response = urllib2.urlopen(url)
	return response.read()

def gpl(outfile):
	# the base link to look at
	f_droid_link = "https://f-droid.org/repository/browse/?fdstyle=grid"

	# the pattern to match
	gpl_pattern1 = "GPL"
	gpl_pattern2 = "General Public License"

	# out filename
	outf = open(outfile, 'w')
	for i in range(1, 20):
	# for i in range(14, 20):
		url =  f_droid_link + "&fdpage=" + str(i) if i > 1 else f_droid_link
		content = download_url(url)
		# res = re.findall(r"https://f-droid.org/repository/browse/\?fdid=[^&]+fdstyle=grid", content)

		"""
		example target:
		https://f-droid.org/repository/browse/?fdid=com.github.wakhub.tinyclock&fdstyle=grid
		"""
		res = re.findall(r"""https://f-droid.org/repository/browse/\?fdid=[^"]+""", content)
		print "There are {0} apps on page: {1}".format(len(res), url)
		for app in res:
			print app
			app_content = download_url(app)
			"""
			example target:
			<b>License:</b> <a href="https://www.gnu.org/licenses/license-list.html#apache2" target="_blank">Apache2</a>
			"""
			app_license = re.findall(r"""<b>License:</b>[^>]+>[^<]+</a>""", app_content)
			# search again, if the first pattern failed
			if len(app_license) == 0:
				app_license = re.findall(r"""<b>License:</b>[^<]+""", app_content)
			if len(app_license) != 1:
				print app
				print app_license
				raise Exception("Wrong number of matches!")
			# find apps that have GPL license
			if ("GPL" in app_license[0]) and ("LGPL" not in app_license[0]):
				outf.write(app + "\n")

def download(infile, outdir):
	gpl_packages = filter(bool, open(infile, 'r').read().split('\n'))
	for package in gpl_packages:
		gpl_content = download_url(package)
		# apk_link = re.findall(r"""<a href="https://f-droid.org/repo/*.apk">download apk</a>""", gpl_content)
		# src_link = re.findall(r"""<a href="https://f-droid.org/repo/*.tar.gz">source tarball</a>""", gpl_content)
		apk_link = re.findall(r"""https://f-droid\.org/repo/[^<]*\.apk(?=")""", gpl_content)
		src_link = re.findall(r"""https://f-droid\.org/repo/[^<]*\.tar\.gz(?=")""", gpl_content)
		print "Processing {0}, apk link is {1} and source link is {2}".format(package, apk_link, src_link)
		# only retrieve the most recent result
		retrieve(apk_link[0], outdir + "/" + apk_link[0].split("/")[-1])
		retrieve(src_link[0], outdir + "/" + src_link[0].split("/")[-1])

def class_names(app_path):
	APP_ROOT = "/".join(app_path.split("/")[:-1])
	return

def find_violation(free, proprietary):
	"""
	Get the total package name
	aapt dump badging net.sf.times_31.apk | grep package:\ name

	find . -name \*.smali

	tree -if --noreport .

	"""
	

	return

def main(argv):
	has_function = False
	help_msg = "re_util.py -f <function> [-o <outfile>], gpl " \
			"[-i <gpl_list> -o <outdir>], download "

	try:
		opts, args = getopt.getopt(argv, "hf:x:y:i:o:", ["function=", 
			"infile=", "outfile="])
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
		else:
			print(help_msg)
			sys.exit(2)
	if not has_function:
		print(help_msg)
		sys.exit()
	if function == "gpl":
		gpl(outfile)
	elif function == "download":
		outdir = outfile
		download(infile, outdir)
	else:
		print(help_msg)
		sys.exit(2)

if __name__ == "__main__":
	main(sys.argv[1:])

