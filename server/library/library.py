from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS
from datetime import datetime
import time, sched
from threading import Timer
from io import BytesIO
from utils import Utils, Settings

class Library:

	class Clip(BytesIO):

		def close(self):
			super().seek(0)
			Utils.dbg(__class__.__name__, "Closing and flushing file")
			lib.saveVideo(self._cameraId, self)
			super().close()

		def setCameraId(self, cameraId):
			self._cameraId = cameraId

		def __init__(self):
			super().__init__()


	def saveVideo(self, cameraId, clipBytes):
		now = datetime.utcnow()
		clipBytes.seek(0)
		f = self._fs.put(clipBytes,
						filename="camera%s-%s.h264" % (cameraId, now),
						contentType="video/H264",
						cameraId=cameraId, 
						saveTime=now)
		Utils.dbg(__class__.__name__, "Saved to file '%s' (filename: '%s')" % (f, "camera%s-%s.h264" % (cameraId, now)))

	def newClip(self):
		return self.Clip()

	def getVideos(self, cameraId=None):
		Utils.dbg(__class__.__name__, "Looking for videos from cameraId: %s" % cameraId)
		if cameraId == None:
			return []
		return list(self._fs.find({"cameraId":cameraId}))

	def getVideo(self, clipId):
		Utils.dbg(__class__.__name__, "Getting video with ID: %s" % clipId)
		return list(self._fs.find({"_id": {'$gt': ObjectId(clipId)}}).limit(2))

	def getCameras(self):
		Utils.dbg(__class__.__name__, "Getting camera list")
		cameras = self._fs.find().distinct("cameraId")
		cameraDetails = {}
		for camera in cameras:
			numberOfVideos = len(self.getVideos(camera))
			cameraDetails[camera] = {
									"cameraId": camera,
									"numberOfVideos": numberOfVideos,
									}
		return cameraDetails

	def __init__(self):
		self._client = MongoClient()
		self._db = self._client.cctv
		self._fs = GridFS(self._db)
		Utils.msg(__class__.__name__, "Initialised connection to MongoDB")

lib = Library()