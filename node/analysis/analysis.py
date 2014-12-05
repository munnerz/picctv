import io
import time
import threading
import picamera
from picamera.array import PiRGBAnalysis
import cv2
import numpy as np
from utils import Utils, Settings

class Analyser:

	def __init__(self):
		self.frames = []
		self.stackLimit = 5
		self._MOTION_LEVEL = 10000
		self._THRESHOLD = 35

	def addFrameToStack(self, frame):
		self.frames.insert(0, frame)
		if len(self.frames) > self.stackLimit:
			self.frames.pop(len(self.frames) - 1)

	def analyse(self, frame):
		self.addFrameToStack(frame)
		if len(self.frames) >= 3:
			motion = self._getMotion()
			if motion and motion[0] > self._MOTION_LEVEL:
				print ("Detected motion level: %d" % motion[0])

	def _getMotion(self):
		d1 = cv2.absdiff(self.frames[1], self.frames[0])
		d2 = cv2.absdiff(self.frames[2], self.frames[0])
		result = cv2.bitwise_and(d1, d2)

		(value, result) = cv2.threshold(result, self._THRESHOLD, 255, cv2.THRESH_BINARY)

		scalar = cv2.sumElems(result)

		#print ("Scalar: %d" % scalar[0])
		return scalar


class Analysis:
	def __init__(self, camera):
		self.thread = threading.Thread(target=self.run)

		self._keepRecording = True
		self._camera = camera
		self.analyser = Analyser()
		self.thread.start()


	def streams(self):
		while self._keepRecording:
			yield self.analyser


	def run(self):
		try:
			while self._keepRecording:
				startTime = time.time()
				#print ("start time %.4f" % startTime)
				stream=open('/run/shm/picamtemp.dat','w+b')
				self._camera.capture(stream, format='yuv', resize=(128,64), use_video_port=True, splitter_port=2)
				frameIndex = self._camera.frame.index
				stream.seek(0)
				self.analyser.analyse(np.fromfile(stream, dtype=np.uint8, count=128*64).reshape((64, 128)))
				endTime = time.time()
				#print ("ended at %.4f (duration: %.4f)" % (endTime, (endTime - startTime)))
				toWait = 0.1 - (endTime - startTime)
				if toWait > 0:
					time.sleep(0.1 - (endTime - startTime))

		except picamera.exc.PiCameraRuntimeError as e:
			Utils.err(self.__class__.__name__, "PiCamera runtime error: %s" % e)
			pass 
