import logging

from picamera import PiVideoFrameType

from modules.ModuleBase import ModuleBase

LOGGER = logging.getLogger("node.Recording")

class Recording(ModuleBase):

	def __init__(self):
		self.buffer = ''

	def required_quality(self):
		return "high"

	def process_frame(self, data):
		(frame, info) = data
		if len(self.buffer) > 1024 * 1024 and info.frame_type == PiVideoFrameType.key_frame:
			toReturn = self.buffer[:]
			self.buffer = frame
			return {"frameData": toReturn, "frame_number": info.index}
		else:
			self.buffer = ''.join((self.buffer, frame))
			return None


	def shutdown(self):
		ModuleBase.shutdown(self)
		LOGGER.info("Shutting down %s" % self.get_name())
		return