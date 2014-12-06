import io
import time
import threading
import picamera
from picamera.array import PiRGBAnalysis
import cv2
import numpy as np
from utils import Utils, Settings
import json

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
		m = 0
		if len(self.frames) >= 3:
			motion = self._getMotion()
			m = motion[0]
			if motion and motion[0] > self._MOTION_LEVEL:
				print ("Detected motion level: %d" % motion[0])
				return (True, m)
		return (False, m)

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
		self._markers = []
		self.analyser = Analyser()
		self.thread.start()


	def getAnalysisBuffer(self, frameNumber):
		for (startFrame, partId, analysisData) in reversed(self._markers):
			if frameNumber >= startFrame:
				print ("returning buffer starting frame ID %d for frame id %d (partId: %s)" % (startFrame, frameNumber, partId))
				return (startFrame, partId, analysisData)
		return None

	def setFrameMarker(self, frameNumber, partId):
		if frameNumber == -1:
			frameNumber = 0
		self._markers.append((frameNumber, partId, []))

	def serialiseChunk(self, buff):
		(startFrame, partId, analysisData) = buff
		return json.dumps({ 
			"startFrame": startFrame,
			"partId": partId,
			"data": analysisData })


	def run(self):
		try:
			time.sleep(3)
			oldBuf = None
			while self._keepRecording:
				startTime = time.time()
				stream=open('/run/shm/picamtemp.dat','w+b') # stored to a ramdisk for faster access
				self._camera.capture(stream, format='yuv', resize=(128,64), use_video_port=True, splitter_port=2)
				frameIndex = self._camera.frame.index # get the current frame index
				stream.seek(0) # seek back to start of captured yuv data
				
				(isMotion, motionVal) = self.analyser.analyse(np.fromfile(stream, dtype=np.uint8, count=128*64).reshape((64, 128)))
				(chunkStartFrame, chunkId, analysisBuffer) = self.getAnalysisBuffer(frameIndex)

				analysisBuffer.append((isMotion, motionVal))

				if not oldBuf == None:
					(oldStartFrame, _, _) = oldBuf
					if chunkStartFrame > oldStartFrame:
						#we need to send the previous buffer off now..!
						print ("Old buffer ready to go - printing:")
						print ("%s" % self.serialiseChunk(oldBuf))
						oldBuf = (chunkStartFrame, chunkId, analysisBuffer)
				else:
					oldBuf = (chunkStartFrame, chunkId, analysisBuffer)

				endTime = time.time()
				toWait = 0.1 - (endTime - startTime)
				if toWait > 0:
					time.sleep(0.1 - (endTime - startTime))

		except picamera.exc.PiCameraRuntimeError as e:
			Utils.err(self.__class__.__name__, "PiCamera runtime error: %s" % e)
			pass 
