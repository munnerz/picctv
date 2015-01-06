from modules.ModuleBase import ModuleBase

class Recording(ModuleBase):

	def required_quality(self):
		return "high"

	def process_frame(self, data):
		(frame, frameInfo) = data

		return len(frame)

	def shutdown(self):
		ModuleBase.shutdown(self)
		print ("Shutting down %s" % self.get_name())
		return