from ModuleBase import ModuleBase
import threading

class Live(ModuleBase):

	def __init__(self):
		ModuleBase.__init__(self) #to ensure the main frame loop begins
		self._listeningThread = threading.Thread(target=self._listen)

		#now start listening...
		self._listeningThread.start()

	def _listen(self):
		return

	def requiredQuality(self):
		return "high"

	def processFrame(self, data):
		(frame, frameInfo) = data
		return len(frame)

	def shutdown(self):
		ModuleBase.shutdown(self)
		print ("Shutting down %s" % self.getName())
		return