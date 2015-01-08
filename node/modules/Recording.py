from modules.ModuleBase import ModuleBase

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
			print ("Ready - sending!")
			return {"frameData": toReturn}
		else:
			print ("Appending frame... (type: %s, len: %d)" % (type(frame), len(frame)))
			self.buffer = ''.join((self.buffer, frame))
			print ("Buffer length: %d" % len(self.buffer))
			return None


	def shutdown(self):
		ModuleBase.shutdown(self)
		print ("Shutting down %s" % self.get_name())
		return