import socket
import threading
import time
import struct
from utils import Utils, Settings

class NetworkManager(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self._connections = []
		self._toExecute = []
		self._running = True
		self._toExecuteLock = threading.Lock()
		self._connectionsToBuffer = Settings.get(__class__.__name__, "connectionsToBuffer")


	def topUpConnections(self):
		while (len(self._connections) < self._connectionsToBuffer):
			Utils.dbg(self.__class__.__name__, "Initialising connection (%d/%d)" % (len(self._connections) + 1, self._connectionsToBuffer))
			con = NetworkConnection()
			if con.connect() != False:
				self._connections.append(con)
			else:
				delay = Settings.get(__class__.__name__, "topUpConnectionRetryDelay")
				Utils.dbg(self.__class__.__name__, "Couldn't connect to server - retrying in %fs" % delay)
				time.sleep(delay)

	# returns the next connection - blocks until it's available
	def connection(self, topUp=True):
		if topUp:
			self.executeLater(lambda: self.topUpConnections())
		try:
			return self._connections.pop(0)
		except IndexError as e:
			delay = Settings.get(__class__.__name__, "connectionRetryDelay")
			Utils.dbg(self.__class__.__name__, "No connections available... waiting for %fs" % delay)
			time.sleep(delay)
			return self.connection(False)

	def executeLater(self, x):
		self._toExecuteLock.acquire()
		self._toExecute.append(x)
		self._toExecuteLock.release()

	def run(self):
		self.topUpConnections()
		Utils.msg(self.__class__.__name__, "Connections to server opened (%d/%d)" % (len(self._connections), self._connectionsToBuffer))
		while self._running:
			Utils.dbg(self.__class__.__name__, "Sweeping for functions to execute")
			nextExec = None
			self._toExecuteLock.acquire()
			try:
				nextExec = self._toExecute.pop(0)
			except IndexError as e:
				nextExec = None
				Utils.dbg(self.__class__.__name__, "Nothing to execute...")
				pass
			finally:
				self._toExecuteLock.release()
			if nextExec != None:
				nextExec()
			time.sleep(Settings.get(__class__.__name__, "functionExecutionSweepDelay"))


class NetworkConnection(threading.Thread):

	def __init__(self, ip='cctv', port=8000):
		self._ip = ip
		self._port = port
		self._connected = False
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.settimeout(2)

	def connect(self):
		try:
			Utils.dbg(self.__class__.__name__, ("Attempting connection to %s:%d" % (self._ip, self._port)) )
			self._sock.connect((self._ip, self._port))

			camera_id = Settings.get(self.__class__.__name__, "cameraId").encode('utf-8')
			self._sock.send(struct.pack("I", len(camera_id)))
			self._sock.send(struct.pack(str(len(camera_id)) + 's', camera_id))

			self._connected = True
			Utils.msg(self.__class__.__name__, "Connected to server.")
		except Exception as e:
			Utils.err(self.__class__.__name__, "Failed to connect to server... exception: %s" % e, False)
			self._connected = False
			return False
		return self._sock

	# get a file object for this network object
	# autoconnect - if true, this function will call connect() if the socket is closed
	def fileObject(self):
		return self._sock.makefile('rwb')

	def stop(self):
		Utils.msg(self.__class__.__name__, "Stopping...")
		if self._connected:
			self._sock.close()
			self._connected = False
		Utils.msg(self.__class__.__name__, "Stopped")