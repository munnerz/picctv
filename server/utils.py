import sys

class Utils:

	className = "Utils"

	def signal_handler(s, signal):
		Utils.dbg(Utils.className, "Signal received")
		sys.exit()

	def msg(sender, text):
		print ("[%s] INFO: %s" % (sender, text))

	def err(sender, text, quit=False):
		print ("[%s] ERROR: %s" % (sender, text))
		if quit:
			Utils.err(Utils.className, "Err quit functionality not added yet", False)

	def dbg(sender, text):
		if Settings.get(Utils.className, "showDebug"):
			print ("[%s] DEBUG: %s" % (sender, text))

class Settings:

	className = "Settings"

	def lookup(a, x, default=lambda x2, y2: Settings.notFound(x2, y2)):
		return a.get(x, default)

	settingMappings = {
				 	"Utils":			lambda x, y: Settings.getUtils(x, y),
				 	"Capture":			lambda x, y: Settings.getCapture(x, y)
					}

	utilsSettings = {
					"showDebug": True,
					"showError": True,
					"showInfo": True,
	}

	captureSettings = {
					"serverPort": 8000,
					"serverIp": "0.0.0.0",
					"chunkSize": 15, #15 chunks, each chunk is currently 4s (60s per chunk)
	}

	def get(owner, name):
		toExec = Settings.lookup(Settings.settingMappings, owner)
		if(toExec != None):
			return toExec(owner, name)

	def getUtils(owner, name):
		m = Settings.lookup(Settings.utilsSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	def getCapture(owner, name):
		m = Settings.lookup(Settings.captureSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	def notFound(owner, name):
		Utils.err(Settings.className, "Setting '%s' for class '%s' not found" % (owner, name))
		return None
