import io
import time
import threading
import picamera
import struct
import socket
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

class AnalysisNetwork:
	def __init__(self):
		self._ip = 'cctv'
		self._port = 7000

		self.thread = threading.Thread(target=self.run)
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.settimeout(2)
		self._sock.connect((self._ip, self._port))
		self._queue = []
		self._queueLock = threading.Lock()
		self.thread.start()

		#TODO: catch exceptions here!!!! URGENT

	def addToQueue(self, d):
		with self._queueLock:
			self._queue.append(d)

	def pop(self):
		with self._queueLock:
			try:
				return self._queue.pop(0)
			except IndexError as e:
				return None

	def run(self):
		try:
			while True:
				toSend = self.pop()
				if toSend == None:
					time.sleep(0.5)
					continue
				data = toSend.encode('utf-8')
				self._sock.send(struct.pack("I", len(data)))
				self._sock.send(struct.pack(str(len(data)) + 's', data))
				print ("Sent analysis data")
		except Exception as e:
			Utils.err(self.__class__.__name__, "I/O Exception %s" % e, False)
		finally:
			self._sock.close()

class Analysis:
	def __init__(self, camera):
		self.thread = threading.Thread(target=self.run)

		self._keepRecording = True
		self._camera = camera
		self._markers = []
		self.analyser = Analyser()
		self._analysisNetwork = AnalysisNetwork()
		self.thread.start()


	def getAnalysisBuffer(self, frameNumber):
		for (startFrame, frameTime, partId, analysisData) in reversed(self._markers):
			if frameNumber >= startFrame:
				return (startFrame, frameTime, partId, analysisData)
		return None

	def setFrameMarker(self, frameNumber, frameTime, partId):
		if frameNumber == -1:
			frameNumber = 0
		self._markers.append((frameNumber, frameTime, partId, []))

	def serialiseChunk(self, buff):
		(startFrame, frameTime, partId, analysisData) = buff
		return json.dumps({ 
			"startFrame": startFrame,
			"partId": partId,
			"motionData": analysisData, 
			"cameraId": Settings.get("NetworkConnection", "cameraId")}) #here we could add different types of analysis data...


	def run(self):
		try:
			time.sleep(3)
			oldBuf = None
			while self._keepRecording:
				startTime = time.time()
				stream=open('/run/shm/picamtemp.dat','w+b') # stored to a ramdisk for faster access
				self._camera.capture(stream, format='yuv', resize=(128,64), use_video_port=True, splitter_port=2)
				timestamp = self._camera.frame.timestamp # get the current frame index - sometimes is None...?
				if timestamp == None:
					time.sleep(0.05)
					timestamp = self._camera.frame.timestamp 
					print ("Reloaded frame index 0.05s later...")
				stream.seek(0) # seek back to start of captured yuv data
				
				(isMotion, motionVal) = self.analyser.analyse(np.fromfile(stream, dtype=np.uint8, count=128*64).reshape((64, 128)))
				
				buf = self.getAnalysisBuffer(timestamp)
				if buf == None: #weird, we may have to drop this block of data (for now...)
					print ("LOST A BUFFER - self.getAnalysisBuffer = None!")
					continue

				(chunkStartFrame, chunkStartTime, chunkId, analysisData) = self.getAnalysisBuffer(timestamp)

				analysisData.append((timestamp, isMotion, motionVal))

				if not oldBuf == None:
					(oldStartFrame, _, _, _) = oldBuf
					if chunkStartFrame > oldStartFrame:
						#we need to send the previous buffer off now..!
						print ("Old buffer ready to go - printing:")
						self._analysisNetwork.addToQueue((self.serialiseChunk(oldBuf)))
						oldBuf = (chunkStartFrame, chunkStartTime, chunkId, analysisData)
				else:
					oldBuf = (chunkStartFrame, chunkStartTime, chunkId, analysisData)

				endTime = time.time()
				toWait = 0.1 - (endTime - startTime)
				if toWait > 0:
					time.sleep(0.1 - (endTime - startTime))

		except picamera.exc.PiCameraRuntimeError as e:
			Utils.err(self.__class__.__name__, "PiCamera runtime error: %s" % e)
			pass 
