import socket
import pickle

from utils import Utils

class Network(object):

	def __init__(self, ip="0.0.0.0", port=8000):
		self._ip = ip
		self._port = port

		self._server_socket = socket.socket()
		self._server_socket.bind((self._ip, self._port))
		self._server_socket.listen(0)
		
		Utils.msg("Network started on %s:%d" % (self._ip, self._port))