import socket
import time
import picamera
from socket import _socketobject, AF_INET, SOCK_STREAM, _fileobject

class FOWrapper(_fileobject):
	def __init__(self, file_):
		self._file = file_

	def write(self, data):
		print 'write'
		try:
			return self._file.write(data)
		except socket.error, e:
			print "caught exception in wrapper"
			raise

	def __getattr__(self, attr):
		return getattr(self._file, attr)


class Capture(object):

	def __init__(self, output, format_='h264', camera = picamera.PiCamera()):
		self._camera = camera
		self._output = output
		self._format = format_

	def configure(self, resolution = (640, 480), framerate = 24):
		self._camera.resolution = resolution
		self._camera.framerate = framerate

	def start(self):
		try:
			self._camera.start_recording(self._output, self._format)
			self._camera.wait_recording(30)
		except:
			raise


	def stop(self):
		self._camera.stop_recording()

def begin():
	try:
		connection = FOWrapper(server_socket.accept()[0].makefile('wb'))
		capture = Capture(connection)
		capture.configure()
		capture.start()
	except socket.error, e:
		pass
		print "socket.errno %d" % e[0]
	    	if(e.errno == 32):
	    		print "connection closed (errno. 32)"
	    		begin()
	    		
	except:
		raise

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8002))
server_socket.listen(0)

connection = FOWrapper(server_socket.accept()[0].makefile('wb'))


try:
	begin()
finally:
	connection.close()
	server_socket.close()