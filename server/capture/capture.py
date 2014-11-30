from library.library import Library
import socket
import threading
import struct
import asyncio
from io import BytesIO

class CaptureStream(threading.Thread):
	def __init__(self, connection, output):
		threading.Thread.__init__(self)
		self._connection = connection
		self._recording = True
		self._output = output

	def run(self):
		try:
			read_bytes = 0
			camera_id_length = struct.unpack("I", self._connection.read(4))[0] #read the camera ID
			camera_id = struct.unpack(str(camera_id_length) + 's', self._connection.read(camera_id_length))[0]
			self._output.setCameraId(camera_id.decode(encoding='UTF-8'))
			while self._recording:
				data = self._connection.read(1024)
				if not data:
					break
				old_read_bytes = read_bytes
				read_bytes += self._output.write(data)
		finally:
			print ("Connections closing")
			self._output.close()
			self._connection.close()

class Capture(threading.Thread):

	def run(self):
		print ("Begin accepting connections...")
		try:
			while True:
				# Accept a single connection and make a file-like object out of it
				connection = self.server_socket.accept()[0].makefile('rb')
				connectionHandler = CaptureStream(connection, self._library.newClip())
				connectionHandler.start()
				print ("Accepted connection")
		finally:
		    self.server_socket.close()
		    print ("Closed socket, capturing stopped")

	def __init__(self, library):
		threading.Thread.__init__(self)
		self._library = library
		print("Started capture")

		sock_addr = ('0.0.0.0', 8001)

		self.server_socket = socket.socket()
		self.server_socket.bind(sock_addr)
		self.server_socket.listen(0)
		print ("Listening for connections on %s:%d" % sock_addr)