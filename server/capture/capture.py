from library import library
import socket
import threading
import struct
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
		self._cameraId = None

	def run(self):
		try:
			read_bytes = 0
			camera_id_length = struct.unpack("I", self._connection.read(4))[0] #read the camera ID
			camera_id = struct.unpack(str(camera_id_length) + 's', self._connection.read(camera_id_length))[0]
			self._cameraId = str(camera_id.decode(encoding='UTF-8'))
			while self._recording:
				data = self._connection.read(1024)
				if not data:
					break
				old_read_bytes = read_bytes
				read_bytes += self._output.write(data)
		finally:
			Utils.dbg(__class__.__name__, "Closing connection...")
			self._output.seek(0)
			self._callback(camera_id, self._output)
			self._connection.close()

class Capture(threading.Thread):

	def run(self):
		Utils.msg(__class__.__name__, "Begin accepting connections...")
		try:
			wholeVideo = []
			while True:
				chunk = BytesIO()
				# Accept a single connection and make a file-like object out of it
				connection = self.server_socket.accept()[0].makefile('rb')
				captureStream = CaptureStream(connection, chunk, lambda x,y: self.recordingFinished(x,y))
				captureStream.start()
				Utils.dbg(__class__.__name__, "Accepted connection")

		finally:
		    self.server_socket.close()
		    Utils.dbg(__class__.__name__, "Closed server socket, no longer accepting connections")

	def recordingFinished(self, cameraId, data):
		self._recordingsLock.acquire()

		ls = self._recordings.get(cameraId, [])
		ls.append(data)
		self._recordings[cameraId] = ls

		Utils.dbg(__class__.__name__, "There are now %d recordings for %s" % (len(self._recordings.get(cameraId)), cameraId))
		
		if len(self._recordings.get(cameraId)) >= Settings.get(__class__.__name__, "chunkSize"):
			listOfClips = self._recordings.pop(cameraId)
			self._recordingsLock.release()
			output = library.lib.newClip()
			output.setCameraId(cameraId)
			for clip in listOfClips:
				output.write(clip.getbuffer())
				clip.close()
			output.close()
		else:
			self._recordingsLock.release()
		

	def __init__(self, library):
		threading.Thread.__init__(self)
		self._library = library
		self._recordingsLock = threading.Lock()
		self._recordings = {}
		sock_addr = (Settings.get(__class__.__name__, "serverIp"), Settings.get(__class__.__name__, "serverPort"))

		self.server_socket = socket.socket()
		self.server_socket.bind(sock_addr)
		self.server_socket.listen(0)
		Utils.dbg(__class__.__name__, "Listening for connections on %s:%d" % sock_addr)
