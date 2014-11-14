import signal
import sys
import socket
import time
import picamera
import queue
import io
from io import BytesIO
import threading

class MultiOutputStream(BytesIO):
	def __init__(self, strm):
		self._str = strm
		self._outputs = {}

	def write(self, data):
		op = self._str.write(data)
		toRemove = []
		for output in self._outputs.keys():
			try:
				output.write(data)
			except Exception as e:
				print ("[Stream] Exception on stream output: %s" % e)
				toRemove.append(output)
		for r in toRemove:
			self.removeOutput(r)
		return op

	def addOutput(self, newo, retry = None):
		print ("[Stream] Adding output of type %s..." % type(newo).__name__)
		self._outputs.update({newo: retry})

	def removeOutput(self, rmo):
		print ("[Stream] Removing output of type %s..." % type(rmo).__name__)
		retry = self._outputs.get(rmo)
		if not retry == None:
			engine.addFunctionToQueue(retry)
		self._outputs.pop(rmo)

	def __getattr__(self, attr):
		return getattr(self._str, attr)


class Capture(threading.Thread):

	def __init__(self, output = MultiOutputStream(io.BytesIO()), format_='h264', camera = picamera.PiCamera()):
		threading.Thread.__init__(self)
		self._camera = camera
		self._output = output
		self._format = format_
		self._keepRecording = True
		self.configure()

	def configure(self, resolution = (1280, 720), framerate = 24):
		self._camera.resolution = resolution
		self._camera.framerate = framerate

	def setOutput(self, output):
		self._output = output

	def run(self):
		print ("[Capture] Starting capturing...")
		if self._output == None:
			return False
		try:
			self._camera.start_recording(self._output, self._format)
		except Exception as e:
			print ("[Capture] Exception raised: %s " % e)
			raise

	def keepRecording(self):
		return self._keepRecording

	def stop(self):
		print ("[Capture] Stopping...")
		self._camera.stop_recording()
		print ("[Capture] Stopped.")


class Engine(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self._engineRunning = True
		self.callback_queue = queue.Queue()

	def run(self):
		print ("[Engine] Engine running...")
		while self._engineRunning:
			callback = self.callback_queue.get()
			if callable(callback):
				callback()
			else:
				print ("[Engine] Uncallable function in engine - discarding!")
			time.sleep(1)

	def addFunctionToQueue(self, func):
		self.callback_queue.put(func)

	def stop(self):
		print ("[Engine] Stopping...")
		self._engineRunning = False
		print ("[Engine] Stopped.")

class Network(object):

	def __init__(self, ip='cctv', port=8000):
		self._ip = ip
		self._port = port
		self._connected = False
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.settimeout(2)

	def connect(self, retry=True):
		if not self.init_connection():
			if retry:
				print ("[Network] Retrying connection...")
				engine.addFunctionToQueue(lambda: network.connect(retry))
			return False
		print ("[Network] Connected to server.")
		capture._output.addOutput(self.fileObject(False), lambda: engine.addFunctionToQueue(network.connect(retry)))

	def init_connection(self):
		try:
			print ("[Network] Attempting connection...")
			self._sock.connect((self._ip, self._port))
			self._connected = True
		except Exception as e:
			print ("[Network] Failed to connect to server... exception type is %s" % e)
			self._connected = False
			return False
		return self._sock

	# get a file object for this network object
	# autoconnect - if true, this function will call connect() if the socket is closed
	def fileObject(self, autoconnect=True):
		if autoconnect:
			if not connect(self):
				return False
		return self._sock.makefile('rwb')

	def stop(self):
		print ("[Network] Stopping...")
		if self._connected:
			self._sock.close()
			self._connected = False
		print ("[Network] Stopped.")


class Utils(object):
	def signal_handler(self, signal):
		network.stop()
		capture.stop()
		engine.stop()
		streamServer.stop()
		print ("Exiting...")
		sys.exit()

class StreamServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.sock_addr = ('0.0.0.0', 8000)

	def listen(self):
		self.server_socket = socket.socket()
		self.server_socket.bind(self.sock_addr)
		self.server_socket.listen(0)
		print ("[StreamServer] Listening...")

	def run(self):
		self.listen()
		while True:
			fos = self.server_socket.accept()[0].makefile('wb')
			print ("[StreamServer] Accepted connection")
			capture._output.addOutput(fos)

	def stop(self):
		print ("[StreamServer] Stopping...")
		self.server_socket.close()
		print ("[StreamServer] Stopped.")

if __name__ == '__main__':
	signal.signal(signal.SIGINT, Utils.signal_handler)

	network = Network()
	engine = Engine()
	capture = Capture()
	streamServer = StreamServer()

	engine.start()

	capture.start()
	network.connect(True)
	streamServer.start()