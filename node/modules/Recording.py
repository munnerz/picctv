import logging

from modules.ModuleBase import ModuleBase

LOGGER = logging.getLogger("node.Recording")

class Recording(ModuleBase):

	def __init__(self):
		self.buffer = ''

	def required_quality(self):
		return "high"

	def process_frame(self, data):
		(frame, info) = data
		if(len(self.buffer) > 1024 * 1024):
			toReturn = self.buffer[:]
			self.buffer = ''
			return {"frameData": toReturn}
		else:
			self.buffer = ''.join((self.buffer, frame))
			return None


	def shutdown(self):
		ModuleBase.shutdown(self)
		LOGGER.info("Shutting down %s" % self.get_name())
		return