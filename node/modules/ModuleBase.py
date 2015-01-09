
class ModuleBase:

	def __init__(self):
		self._stack = []
		self._running = True

	@classmethod
	def get_name(cls):
		return cls.__name__

	def required_quality(self):
		raise NotImplementedError("Module doesn't specify it's required quality")

	def process_frame(self, data):
		raise NotImplementedError("Module doesn't implement a processFrame method")

	def shutdown(self):
		return
