import threading
import socket
import time

class StreamServer(threading.Thread):
	def __init__(self, multiplexer=None):
		threading.Thread.__init__(self)
		self.sock_addr = ('0.0.0.0', 8000)
		self.multiplexer = multiplexer

	def listen(self):
		self.server_socket = socket.socket()
		self.server_socket.bind(self.sock_addr)
		self.server_socket.listen(0)
		print ("[StreamServer] Listening...")

	def run(self):
		self.listen()
		while True:
			if self.multiplexer == None:
				time.sleep(2)
				continue
			fos = self.server_socket.accept()[0].makefile('wb')
			print ("[StreamServer] Accepted connection")
			self.multiplexer.addOutput(fos)

	def stop(self):
		print ("[StreamServer] Stopping...")
		self.server_socket.close()
		print ("[StreamServer] Stopped.")