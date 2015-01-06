from ModuleBase import ModuleBase
import threading, socket

class Live(ModuleBase):

	def __init__(self):
		ModuleBase.__init__(self) #to ensure the main frame loop begins
		self._sock_addr = ('0.0.0.0', 8000)
		self._keepListening = True
		self._listeningThread = threading.Thread(target=self._listen)

		self._outputs = []
		self._outputLock = threading.Lock()

		#now start listening...
		self._listeningThread.start()


	def _listen(self):
		self._server_socket = socket.socket()
		self._server_socket.bind(self._sock_addr)
		self._server_socket.listen(0)

		while self._keepListening:
			fos = self._server_socket.accept()[0].makefile('wb')
			with self._outputLock:
				self._outputs.append(fos)
		return

	def requiredQuality(self):
		return "high"

	def processFrame(self, data):
		(frame, frameInfo) = data
		with self._outputLock:
			for output in self._outputs[:]:
				try:
					print ("Writing...")
					output.write(frame)
				except Exception as e:
					print ("Exception in Live module during processFrame: %s" % e)
					self._outputs.remove(output)
					pass
		return len(frame)

	def shutdown(self):
		ModuleBase.shutdown(self)
		self._keepListening = False
		self._server_socket.close()
		print ("Shutting down %s" % self.getName())
		return