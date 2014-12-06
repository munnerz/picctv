import socket
import threading
from io import BytesIO
import json
import struct

class AnalysisReader(threading.Thread):
	def __init__(self, connection, library):
		threading.Thread.__init__(self)
		self._connection = connection
		self._library = library

	def run(self):
		try:
			while True:
				self._read_bytes = 0
				data_len = struct.unpack("I", self._connection.read(4))[0] #read the camera ID
				data = struct.unpack(str(data_len) + 's', self._connection.read(data_len))[0]
				data = str(data.decode(encoding='UTF-8'))
				toStore = json.loads(data)
				self._library.saveAnalysisData(toStore.get('cameraId'), toStore.get('partId'), toStore)
		finally:
			self._connection.close()

class Analysis(threading.Thread):

	def __init__(self, library):
		threading.Thread.__init__(self)
		self.library = library
		sock_addr = ('0.0.0.0', 7000)
		#sock_addr = (Settings.get(__class__.__name__, "serverIp"), Settings.get(__class__.__name__, "serverPort"))
		self.server_socket = socket.socket()
		self.server_socket.bind(sock_addr)
		self.server_socket.listen(0)

	def run(self):
		try:
			while True:
				# Accept a single connection and make a file-like object out of it
				connection = self.server_socket.accept()[0].makefile('rb')
				rdr = AnalysisReader(connection, self.library)
				rdr.start()
		finally:
			self.server_socket.close()
