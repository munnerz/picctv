from ModuleBase import ModuleBase

class Motion(ModuleBase):

	def requiredQuality(self):
		return "low"

	def processFrame(self, data):
		(frame, frameInfo) = data
		return len(frame)

	def shutdown(self):
		ModuleBase.shutdown(self)
		print ("Shutting down %s" % self.getName())
		return