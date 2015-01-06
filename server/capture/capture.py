from library import library
import socket
import threading
import struct, pickle
import asyncio
from io import BytesIO
from utils import Utils, Settings

class CaptureStream(threading.Thread):
	def __init__(self, connection, output, callback):
		threading.Thread.__init__(self)
		self._connection = connection
		self._recording = True
		self._output = output
		self._callback = callback
		self.camera_name = None
		self._chunkId = 0
		self.module_name = None
		self._read_bytes = 0

	def run(self):
		try:
			self._read_bytes = 0

			camera_name_length = struct.unpack("I", self._connection.read(4))[0] #read the camera ID
			camera_name_pickled = struct.unpack(str(camera_name_length) + 's', self._connection.read(camera_name_length))[0]
			self.camera_name = pickle.loads(camera_name_pickled)

			module_name_length = struct.unpack("I", self._connection.read(4))[0] #read the chunk ID
			module_name_pickled = struct.unpack(str(module_name_length) + 's', self._connection.read(module_name_length))[0]
			self.module_name = pickle.loads(module_name_pickled)

			print ("Camera name: %s, module name: %s" % (self.camera_name, self.module_name))
			while self._recording:
				data = self._connection.read(1024)
				if not data:
					break
				old_read_bytes = self._read_bytes
				self._read_bytes += self._output.write(data)
		finally:
			Utils.dbg(self.__class__.__name__, "Closing connection...")
			self._output.seek(0)
			self._callback(self)
			self._connection.close()

class Capture(threading.Thread):

	def run(self):
		Utils.msg(self.__class__.__name__, "Begin accepting connections...")
		try:
			wholeVideo = []
			while True:
				Utils.dbg(self.__class__.__name__, "There are %d open connections" % len(self._connections))
				chunk = BytesIO()
				# Accept a single connection and make a file-like object out of it
				connection = self.server_socket.accept()[0].makefile('rb')
				captureStream = CaptureStream(connection, chunk, lambda x: self.recordingFinished(x))
				captureStream.start()
				self._connectionsLock.acquire()
				self._connections.append(captureStream)
				self._connectionsLock.release()
				Utils.dbg(self.__class__.__name__, "Accepted connection")

		finally:
		    self.server_socket.close()
		    Utils.dbg(self.__class__.__name__, "Closed server socket, no longer accepting connections")

	def recordingFinished(self, outputStream):
		self._connectionsLock.acquire()
		self._connections.remove(outputStream)
		self._connectionsLock.release()
		
		cameraId = outputStream.camera_name
		self._recordingsLock.acquire()

		ls = self._recordings.get(cameraId, [])
		ls.append(outputStream)
		self._recordings[cameraId] = ls

		Utils.dbg(self.__class__.__name__, "There are now %d recordings for %s" % (len(self._recordings.get(cameraId)), cameraId))
		
		flush = False
		if(outputStream._read_bytes == 0 and len(ls) > 1):
			Utils.dbg(self.__class__.__name__, "Received a zero length buffer from a node. Saving all chunks...")
			flush = True
		if flush or len(self._recordings.get(cameraId)) >= Settings.get(self.__class__.__name__, "chunkSize"):
			listOfClips = self._recordings.pop(cameraId)
			self._recordingsLock.release()
			dboutput = library.lib.newClip()
			dboutput.setCameraId(cameraId)
			chunkIds = []
			for clip in listOfClips:
				chunkIds.append(clip._chunkId)
				dboutput.write(clip._output.getbuffer())
				clip._output.close()
			dboutput.setChunkIds(chunkIds)
			dboutput.close()
		else:
			self._recordingsLock.release()
		

	def __init__(self, library):
		threading.Thread.__init__(self)
		self._library = library
		self._recordingsLock = threading.Lock()
		self._connectionsLock = threading.Lock()
		self._recordings = {}
		self._connections = []
		sock_addr = (Settings.get(self.__class__.__name__, "serverIp"), Settings.get(self.__class__.__name__, "serverPort"))

		self.server_socket = socket.socket()
		self.server_socket.bind(sock_addr)
		self.server_socket.listen(0)

		Utils.dbg(self.__class__.__name__, "Listening for connections on %s:%d" % sock_addr)
