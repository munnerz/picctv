import signal
import sys
import socket
import time
import picamera
import io
from io import BytesIO
import threading

class MultiOutputStream(BytesIO):
	def __init__(self, strm):
		self._str = strm
		self._secondary = None
		self._outputs = []

	def write(self, data):
		op = self._str.write(data)
		for output in self._outputs:
			try:
				output.write(data)
			except Exception, e:
				print "Error code: %d" % e[0]
				self.removeOutput(output)
		return op

	def addOutput(self, newo):
		print "Adding output of type %s..." % type(newo).__name__
		self._outputs.append(newo)

	def removeOutput(self, rmo):
		print "Removing output of type %s..." % type(rmo).__name__
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

	def configure(self, resolution = (1280, 720), framerate = 24):
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

def signal_handler(self, signal):
	print "quit"
	capture.stop()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

stream = MultiOutputStream(io.BytesIO())
capture = Capture(stream)
capture.configure()
capture.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('cctv', 8000))

stream.addOutput(sock.makefile('rw'))