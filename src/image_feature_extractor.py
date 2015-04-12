"""
Extract different types of features from an image and store them 
into proto bufffer.
"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import cv2
# import cv2.cv as cv
import numpy as np
import tesseract
import proto.image_features_pb2 as ifp
from matplotlib import pyplot as plt

class FeatureExtractor:
	def __init__(self, feature_extractor_config):
		self.all_images = ifp.AllImages()
		self.all_images.extractor_config.CopyFrom(feature_extractor_config)
		self.image_feature_dict = dict()

	def extract(self, image_path):
		image = self.all_images.image.add()
		image.path = image_path 
		feature = image.image_feature.add()
		if self.all_images.extractor_config.harris_corner:
			feature.type = ifp.ImageFeature.HarrisCorner
			kp, des = self.extract_harris_corner(image)
		if self.all_images.extractor_config.shitomasi_corner:
			feature.type = ifp.ImageFeature.ShiTomasiCorner
			kp, des = self.extract_shitomasi_corner(image)
		if self.all_images.extractor_config.sift:
			feature.type = ifp.ImageFeature.SIFT
			kp, des = self.extract_sift(image)
		if self.all_images.extractor_config.surf:
			feature.type = ifp.ImageFeature.SURF
			kp, des = self.extract_surf(image)
		if self.all_images.extractor_config.fast:
			feature.type = ifp.ImageFeature.FAST
			kp, des = self.extract_fast(image)
		if self.all_images.extractor_config.brief:
			feature.type = ifp.ImageFeature.BRIEF
			kp, des = self.extract_brief(image)
		if self.all_images.extractor_config.orb:
			feature.type = ifp.ImageFeature.ORB
			kp, des = self.extract_orb(image)
		if self.all_images.extractor_config.ocr:
			feature.type = ifp.ImageFeature.OCR
			kp, des = self.extract_ocr(image)
		if des is None:
			return
		for i in range(len(kp)):
			key_value = feature.key_value.add()
			key_value.kp.x = kp[i].pt[0]
			key_value.kp.y = kp[i].pt[1]
			#key_value.des = des[i].tobytes()
			key_value.des = des[i].tostring()
			# print des[i]
			# print key_value.des
		self.image_feature_dict[image.path] = [image.path, kp, des]
		# add more features

	def extract_harris_corner(self, image):
		img = cv2.imread(image.path)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = np.float32(gray)
		dst = cv2.cornerHarris(gray,2,3,0.04)

		#result is dilated for marking the corners, not important
		dst = cv2.dilate(dst, None)

		# Threshold for an optimal value, it may vary depending on the image.
		img[dst>0.01*dst.max()] = [0,0,255]

		cv2.imshow('dst',img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		return dst, None
	
	def extract_shitomasi_corner(self, image):
		# params for ShiTomasi corner detection
		feature_params = dict(maxCorners = 100, qualityLevel = 0.3,
				minDistance = 7, blockSize = 7)
		"""
		reference:
		http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html
		corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
		"""
		img = cv2.imread(image.path)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		corners = cv2.goodFeaturesToTrack(gray, mask = None, **feature_params)
		corners = np.int0(corners)

		for i in corners:
			x,y = i.ravel()
			cv2.circle(img,(x,y),3,255,-1)
		plt.imshow(img), plt.show()

		return corners, None

	def extract_sift(self, image):
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
		sift = cv2.Feature2D_create("SIFT")
		kp, des = sift.detectAndCompute(img, None)
		img = cv2.drawKeypoints(img, kp)
		cv2.imwrite(image.path + '.sift.png', img)
		return kp, des
	
	def extract_surf(self, image):
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)

		# surf = cv2.Feature2D_create("SURF")
		# reduce the number of keypoints
		surf = cv2.SURF()
		
		surf.hessianThreshold = 400
		kp, des = surf.detectAndCompute(img, None)

		img = cv2.drawKeypoints(img, kp, None, (255,0,0), 4)
		cv2.imwrite(image.path + '.surf.png', img)
		return kp, des

	def extract_fast(self, image):
		"""
		FAST is simply extracting key points, we need a feature descriptor for it.
		Here we use BRIEF as the descriptor.
		"""
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
		# Initiate FAST object with default values
		fast = cv2.FastFeatureDetector()
		# find and draw the keypoints
		kp = fast.detect(img,None)
		brief = cv2.DescriptorExtractor_create("BRIEF")
		# compute the descriptors with BRIEF
		kp, des = brief.compute(img, kp)
		img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
		cv2.imwrite(image.path + '.fast.png', img2)
		"""
		# Disable nonmaxSuppression
		fast.setBool('nonmaxSuppression',0)
		kp = fast.detect(img,None)

		print "Total Keypoints without nonmaxSuppression: ", len(kp)

		img3 = cv2.drawKeypoints(img, kp, color=(255,0,0))

		cv2.imwrite('fast_false.png',img3)
		"""
		return kp, des 
	
	def extract_brief(self, image):
		"""
		START works badly in our case.
		"""
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
		# Initiate STAR detector
		star = cv2.FeatureDetector_create("STAR")
		# star = cv2.FeatureDetector_create("SIFT")
		# Initiate BRIEF extractor
		brief = cv2.DescriptorExtractor_create("BRIEF")
		# find the keypoints with STAR
		kp = star.detect(img, None)
		# compute the descriptors with BRIEF
		kp, des = brief.compute(img, kp)
		img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
		cv2.imwrite(image.path + '.brief.png', img2)
		"""
		print image.path
		print brief.getInt('bytes')
		print des.shape
		"""
		return kp, des

	def extract_orb(self, image):
		"""
		Better version of BRIEF and FAST.
		"""
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
		# Initiate STAR detector
		orb = cv2.ORB()
		# find the keypoints and compute descriptors with ORB
		kp, des = orb.detectAndCompute(img, None)
		# draw only keypoints location, not size and orientation
		img2 = cv2.drawKeypoints(img,kp,color=(0,255,0), flags=0)
		plt.imshow(img2),plt.show()
		return kp, des
	
	def extract_ocr(self, image):
		# this one is broken
		print image.path
		api = tesseract.TessBaseAPI()
		api.Init(".", "eng", tesseract.OEM_DEFAULT)
		api.SetPageSegMode(tesseract.PSM_AUTO)
		image = cv.LoadImage(image.path, cv.CV_LOAD_IMAGE_GRAYSCALE)
		tesseract.SetCvImage(image, api)
		text = api.GetUTF8Text()
		conf = api.MeanTextConf()
		api.End()
		print text
		return text

class ImageMatcher:
	def __init__(self, image_matcher_config=None):
		self.image_matcher_config = ifp.ImageMatcherConfig()
		if image_matcher_config:
			self.image_matcher_config.CopyFrom(image_matcher_config)

	def patch_find_match(self, image_feature_dict_A, image_feature_dict_B):
		"""
		image_feature_dict is a mapping from image path to
		keypoints and descriptions.
		e.g.
		image_feature_dict_A[path] = [kp, des]

		@parameter
		image_feature_dict_A: the first set of image
		image_feature_dict_B: the second set of image
		"""
		for path_A in image_feature_dict_A:
			for path_B in image_feature_dict_B:
				self.find_match(image_feature_dict_A[path_A],
						image_feature_dict_B[path_B])

	def find_match(self, image_A, image_B):
		path1, kp1, des1 = image_A
		path2, kp2, des2 = image_B
		img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
		img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)
		match = False
		try:
			match = self.match_des(des1, des2)
		except:
			temp = des1
			des1 = des2
			des2 = temp
			match = self.match_des(des1, des2)

		if match:
			print "{0}, {1} matches!".format(path1, path2)
		# Brute-Force Matching with SIFT Descriptors and Ratio Test

		"""
		for m in matches:
			if m.distance < 200:
				print m.distance
				good.append([m])
		if len(kp1) > 20 and len(kp2) > 20 and len(good) > 10:
			print "{0}, {1} matches!".format(path1, path2)
			print "kp# for image 1 is {0}, kp# for image " \
					"2 is {1}, matches {2}".format(len(kp1),
							len(kp2), len(good))
		"""

		# cv2.drawMatchesKnn expects list of lists as matches.
		img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, flags=2)
		plt.imshow(img3),plt.show()

	def match_des(self, des1, des2):
		MIN_MATCH_COUNT = 5 

		# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		bf = cv2.BFMatcher()
		matches = bf.knnMatch(des1, des2, k=2)
		"""
		# FLANN based matches
		FLANN_INDEX_KDTREE = 0
		index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
		search_params = dict(checks = 50)
		flann = cv2.FlannBasedMatcher(index_params, search_params)
		matches = flann.knnMatch(des1,des2,k=2)
		"""
		# Apply ratio test
		good = []
		for m, n in matches:
			if m.distance < 0.75 * n.distance:
				good.append([m])
		print len(des1), len(des2), len(good)
		if len(good) > MIN_MATCH_COUNT:
			return True
		else:
			# print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
			matchesMask = None
			return False

