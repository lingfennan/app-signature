"""
Extract different types of features from an image and store them 
into proto bufffer.
"""
# Author: Ruian Duan
# Contact: duanruian@gmail.com

import cv2
import numpy as np
import proto.image_features_pb2 as ifp
from matplotlib import pyplot as plt

class FeatureExtractor:
	def __init__(self, feature_extractor_config):
		self.all_images = ifp.AllImages()
		self.all_images.extractor_config.CopyFrom(feature_extractor_config)

	def extract(self, image_path):
		image = self.all_images.image.add()
		image.path = image_path
		if self.all_images.extractor_config.harris_corner:
			self.extract_harris_corner(image)
		if self.all_images.extractor_config.shitomasi_corner:
			self.extract_shitomasi_corner(image)
		if self.all_images.extractor_config.sift:
			self.extract_sift(image)
		if self.all_images.extractor_config.surf:
			self.extract_surf(image)
		if self.all_images.extractor_config.fast:
			self.extract_fast(image)
		if self.all_images.extractor_config.brief:
			self.extract_brief(image)
		if self.all_iamges.extractor_config.orb:
			self.extract_orb(image)
		# add more features

	def extract_harris_corner(self, image):
		img = cv2.imread(image.path)
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = np.float32(gray)
		dst = cv2.cornerHarris(gray,2,3,0.04)

		#result is dilated for marking the corners, not important
		dst = cv2.dilate(dst,None)

		# Threshold for an optimal value, it may vary depending on the image.
		img[dst>0.01*dst.max()]=[0,0,255]

		cv2.imshow('dst',img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		image_feature = image.image_feature.add()
		image_feature.type = ifp.ImageFeature.HarrisCorner
		key_value = image_feature.key_value.add()
	
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

		image_feature = image.image_feature.add()
		image_feature.type = ifp.ImageFeature.HarrisCorner
		key_value = image_feature.key_value.add()

	def extract_sift(self, image):
		img = cv2.imread(image.path)
		gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

		sift = cv2.SIFT()
		# sift = cv2.SIFT_create()
		kp, des = sift.detectAndCompute(gray,None)
		img = cv2.drawKeypoints(gray,kp)

		image_feature = image.image_feature.add()
		image_feature.type = ifp.ImageFeature.HarrisCorner
		key_value = image_feature.key_value.add()
	
	def extract_surf(self, image):
		img = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
		surf = cv2.SURF(400)
		# reduce the number of keypoints
		surf.hessianThreshold = 50000
		kp, des = surf.detectAndCompute(img,None)

		img2 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)
		plt.imshow(img2),plt.show()

		image_feature = image.image_feature.add()
		image_feature.type = ifp.ImageFeature.HarrisCorner
		key_value = image_feature.key_value.add()
	
	def extract_fast(self, image):
		img = cv2.imread('simple.jpg',0)

		# Initiate FAST object with default values
		fast = cv2.FastFeatureDetector()

		# find and draw the keypoints
		kp = fast.detect(img,None)
		img2 = cv2.drawKeypoints(img, kp, color=(255,0,0))

		# Print all default params
		print "Threshold: ", fast.getInt('threshold')
		print "nonmaxSuppression: ", fast.getBool('nonmaxSuppression')
		print "neighborhood: ", fast.getInt('type')
		print "Total Keypoints with nonmaxSuppression: ", len(kp)

		cv2.imwrite('fast_true.png',img2)

		# Disable nonmaxSuppression
		fast.setBool('nonmaxSuppression',0)
		kp = fast.detect(img,None)

		print "Total Keypoints without nonmaxSuppression: ", len(kp)

		img3 = cv2.drawKeypoints(img, kp, color=(255,0,0))

		cv2.imwrite('fast_false.png',img3)
	
	def extract_brief(self, image):
		img = cv2.imread('simple.jpg',0)
		# Initiate STAR detector
		star = cv2.FeatureDetector_create("STAR")
		# Initiate BRIEF extractor
		brief = cv2.DescriptorExtractor_create("BRIEF")
		# find the keypoints with STAR
		kp = star.detect(img, None)
		# compute the descriptors with BRIEF
		kp, des = brief.compute(img, kp)
		print brief.getInt('bytes')
		print des.shape

	def extract_orb(self, image):
		# Initiate STAR detector
		orb = cv2.ORB()

		# find the keypoints with ORB
		kp = orb.detect(img,None)

		# compute the descriptors with ORB
		kp, des = orb.compute(img, kp)

		# draw only keypoints location,not size and orientation
		img2 = cv2.drawKeypoints(img,kp,color=(0,255,0), flags=0)
		plt.imshow(img2),plt.show()




