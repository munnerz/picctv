import io
import time
import threading
import picamera
from picamera.array import PiRGBAnalysis
import cv2
import numpy as np
from utils import Utils, Settings

class Analyser(PiRGBAnalysis):

	def __init__(self, camera):
		PiRGBAnalysis.__init__(self, camera)
		self.frames = []
		self.stackLimit = 5
		self._MOTION_LEVEL = 500000
		self._THRESHOLD = 35

	def addFrameToStack(self, frame):
		self.frames.insert(0, frame)
		if len(self.frames) > self.stackLimit:
			self.frames.pop(len(self.frames) - 1)

	def analyse(self, frame):
		cv2.imshow('image',frame)
		self.addFrameToStack(frame)
		if len(self.frames) >= 3:
			motion = self._getMotion()
			if motion and motion[0] > self._MOTION_LEVEL:
				print ("Detected motion!")

	def _getMotion(self):
		d1 = cv2.absdiff(self.frames[1], self.frames[0])
		d2 = cv2.absdiff(self.frames[2], self.frames[0])
		result = cv2.bitwise_and(d1, d2)

		(value, result) = cv2.threshold(result, self._THRESHOLD, 255, cv2.THRESH_BINARY)

		scalar = cv2.sumElems(result)

		print (" - scalar:", scalar[0], scalar)
		return scalar


class Analysis:
	def __init__(self, camera):
		self.thread = threading.Thread(target=self.run)

		self._keepRecording = True
		self._camera = camera
		self.analyser = Analyser(self._camera)

		self.thread.start()


	def streams(self):
		while self._keepRecording:
			yield self.analyser


	def run(self):
		self._camera.capture_sequence(self.streams(), format='bgr', use_video_port=True, resize=(1280,720), splitter_port=2)
		cv2.destroyAllWindows()


