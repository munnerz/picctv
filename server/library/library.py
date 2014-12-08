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
			Utils.dbg(self.__class__.__name__, "Closing and flushing file")
			if(self.tell() == 0):
				Utils.dbg(self.__class__.__name__, "Discarding empty Clip")
			else:
				super().seek(0)
				lib.saveVideo(self)
			super().close()

		def setCameraId(self, cameraId):
			self._cameraId = cameraId

		def setChunkIds(self, chunkIds):
			self._chunkIds = chunkIds

		def __init__(self):
			super().__init__()


	def saveVideo(self, clipBytes):
		now = datetime.utcnow()
		clipBytes.seek(0)
		d = Utils.h264ToMP4(clipBytes)
		if d != None:
			f = self._fs.put(d,
							filename="camera%s-%s.h264" % (clipBytes._cameraId, now),
							contentType="video/mp4",
							cameraId=clipBytes._cameraId, 
							chunkIds=clipBytes._chunkIds,
							saveTime=now)


			Utils.dbg(self.__class__.__name__, "Saved to file '%s' (filename: '%s')" % (f, "camera%s-%s.h264" % (clipBytes._cameraId, now)))
			d.close()
		else:
			Utils.msg(self.__class__.__name__, "Invalid ffmpeg output - skipping recording...")

	def saveAnalysisData(self, cameraId, partId, data):
		movements = 0
		for (_, motion, _) in data.get('motionData'):
			if motion:
				movements += 1
		data['numberOfMotionEvents'] = movements
		self._db.analysis.insert({'cameraId':cameraId, 'chunkId':partId, 'motionData':data})

	def newClip(self):
		return self.Clip()

	def getVideos(self, cameraId=None):
		Utils.dbg(__class__.__name__, "Looking for videos from cameraId: %s" % cameraId)
		if cameraId == None:
			return []
		return list(self._fs.find({"cameraId":cameraId}))

	def numberOfMotionEvents(self, clipId):
		''' caclulates the number of motion events in a given clip (spanning multiple chunks) '''
		clip = list(self._fs.find({"_id": ObjectId(clipId)}))[0]
		chunks = clip.chunkIds
		return self.motionsInChunks(chunks)

	def motionsInChunks(self, chunkIds):
		chunks = self._db.analysis.find({ 'chunkId' : { '$in' : chunkIds } })
		total = 0
		for chunk in chunks:
			total += chunk.get('motionData').get('numberOfMotionEvents')
		return total

	def motionsInChunk(self, chunkId):
		print ("searcing for %s" % chunkId)
		chunkData = self._db.analysis.find_one({'chunkId': chunkId})
		if chunkData == None:
			return 0
		return chunkData.get('motionData').get('numberOfMotionEvents')

	def getVideo(self, clipId, limit=2):
		cameraId = list(self._fs.find({"_id": ObjectId(clipId)}))[0].cameraId

		return list(self._fs.find({"_id": {'$gte': ObjectId(clipId)}, "cameraId": cameraId}).limit(limit))

	def getCameras(self):
		Utils.dbg(self.__class__.__name__, "Getting camera list")
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
		Utils.msg(self.__class__.__name__, "Initialised connection to MongoDB")

lib = Library()