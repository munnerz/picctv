import socket
import time
import picamera
import io
import signal
import sys
from io import BytesIO
import threading
from socket import _socketobject, AF_INET, SOCK_STREAM, _fileobject

class IOWrapper(BytesIO):
	def __init__(self, strm):
		self._str = strm
		self._secondary = None
		self._outputs = []

	def write(self, data):
		op = self._str.write(data)
		for output in self._outputs:
			try:
				output.write(data)
			except socket.error, e:
				print "Error code: %d" % e[0]
				self._outputs.remove(output)
		return op

	def addOutput(self, newo):
		self._outputs.append(newo)

	def removeOutput(self, rmo):
		self._outputs.remove(rmo)

	def __getattr__(self, attr):
		return getattr(self._str, attr)


class Capture(threading.Thread):

	def __init__(self, output = None, format_='h264', camera = picamera.PiCamera()):
		threading.Thread.__init__(self)
		self._camera = camera
		self._output = output
		self._format = format_
		self._keepRecording = True

	def configure(self, resolution = (640, 480), framerate = 24):
		self._camera.resolution = resolution
		self._camera.framerate = framerate

	def setOutput(self, output):
		self._output = output

	def run(self):
		print "Starting capturing..."
		if self._output == None:
			return False
		try:
			self._camera.start_recording(self._output, self._format)
			while True:
				self._camera.wait_recording(30)
		except:
			raise

	def keepRecording(self):
		return True

	def stop(self):
		self._camera.stop_recording()

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8002))
server_socket.listen(0)

stream = IOWrapper(io.BytesIO())
capture = Capture(stream)
capture.daemon = True
capture.configure()
capture.start()

while True:
	connection = server_socket.accept()[0].makefile('wb')
	stream.addOutput(connection)