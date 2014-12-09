from threading import Thread, Condition, Lock

class ModuleBase:

	def __init__(self):
		self._thread = Thread(None, self._run, self.getName())
		self._stackLock = Lock()
		self._stackCondition = Condition(self._stackLock)
		self._stack = []
		self._running = True
		self._thread.start()

	def _addFrameToStack(self, frame, frameInfo):
		with self._stackCondition:
			self._stack.append((frame, frameInfo))
			self._stackCondition.notifyAll()

	def _run(self):
		while self._running:
			with self._stackCondition:
				if len(self._stack) == 0:
					self._stackCondition.wait() # (0.02 = 50 FPS, more than enough)
				try:
					self.processFrame(self._stack.pop(0))
				except Exception as e:
					print ("Error in %s module: %s" % e)
					raise #TODO: Change this to pass to ensure no modules crash (or perhaps this makes sense?)

	@classmethod
	def getName(cls):
		return cls.__name__

	def requiredQuality(self):
		raise NotImplementedError("Module doesn't specify it's required quality")

	def processFrame(self, data):
		raise NotImplementedError("Module doesn't implement a processFrame method")

	def shutdown(self):
		self._running = False