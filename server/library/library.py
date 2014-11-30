from pymongo import MongoClient
from gridfs import GridFS
from datetime import datetime
from config import Config
from library.tables import *
import time, sched
from threading import Timer
from io import BytesIO


class Library:

	class Clip(BytesIO):

		def close(self):
			super().seek(0)
			print ("Closed file")
			self._library.saveVideo(self._cameraId, self)
			super().close()

		def setCameraId(self, cameraId):
			self._cameraId = cameraId

		def __init__(self, library):
			super().__init__()
			self._library = library


	def getDefaultLibrary():
		print("Getting default")
		return Library()

	def saveVideo(self, cameraId, clipBytes):
		now = datetime.utcnow()
		clipBytes.seek(0)
		f = self._fs.put(clipBytes,
						filename="camera%s-%s.h264" % (cameraId, now),
						contentType="video/H264",
						camera_id=cameraId, 
						save_time=now)
		print("Saved: %s" % f)

	def newClip(self):
		return self.Clip(self)

	def getVideos(self, cameraId=None):
		return None

	def __init__(self):
		self._client = MongoClient()
		self._db = self._client.cctv
		self._fs = GridFS(self._db)
		print("Initialised cctv db")