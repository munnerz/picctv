
class ModuleBase:

	def __init__(self):
		self._stack = []
		self._running = True

	@classmethod
	def getName(cls):
		return cls.__name__

	def newKeyFrameDetected(self, keyFrame, keyFrameInfo):
		return False

	def requiredQuality(self):
		raise NotImplementedError("Module doesn't specify it's required quality")

	def processFrame(self, data):
		raise NotImplementedError("Module doesn't implement a processFrame method")

	def shutdown(self):
		self._running = False