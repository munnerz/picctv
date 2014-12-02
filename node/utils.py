import sys
import inspect

class Utils:

	className = "Utils"

	@classmethod
	def signal_handler(ut, s, signal):
		Utils.dbg(Utils.className, "Signal received")
		sys.exit()

	@classmethod
	def msg(ut, sender, text):
		print ("[%s] INFO: %s" % (sender, text))

	@classmethod
	def err(ut, sender, text, quit=False):
		print ("[%s] ERROR: %s" % (sender, text))
		if quit:
			Utils.err(Utils.className, "Err quit functionality not added yet", False)

	@classmethod
	def dbg(ut, sender, text):
		if Settings.get(Utils.className, "showDebug"):
			print ("[%s] DEBUG: %s" % (sender, text))

	@classmethod
	def dbg2(ut, sender, text):
		if Settings.get(Utils.className, "showDebug2"):
			print ("[%s] DEBUG2: %s" % (sender, text))

class Settings:

	@classmethod
	def lookup(sc, a, x, default=lambda x2, y2: Settings.notFound(x2, y2)):
		return a.get(x, default)

	settingMappings = {
					"NetworkManager": 	lambda x, y: Settings.getNetworkManager(x, y),
				 	"Capture":			lambda x, y: Settings.getCapture(x, y),
				 	"Utils":			lambda x, y: Settings.getUtils(x, y),
				 	"NetworkConnection":lambda x, y: Settings.getNetworkConnection(x, y),
					}

	networkManagerSettings = {
					"connectionsToBuffer" : 3,
			  		"connectionRetryDelay": 1,
			  		"functionExecutionSweepDelay": 0.5,
	}

	captureSettings = {
					"chunkLength": 4,
	}

	utilsSettings = {
					"showDebug2": False,
					"showDebug": True,
					"showError": True,
					"showInfo": True,
	}

	networkConnectionSettings = {
					"cameraId": "Front Door",
	}

	@classmethod
	def get(sc, owner, name):
		toExec = Settings.lookup(Settings.settingMappings, owner)
		if(toExec != None):
			return toExec(owner, name)

	@classmethod
	def getNetworkManager(sc, owner, name):
		m = Settings.lookup(Settings.networkManagerSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@classmethod
	def getCapture(sc, owner, name):
		m = Settings.lookup(Settings.captureSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@classmethod
	def getUtils(sc, owner, name):
		m = Settings.lookup(Settings.utilsSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@classmethod
	def getNetworkConnection(sc, owner, name):
		m = Settings.lookup(Settings.networkConnectionSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@classmethod
	def notFound(sc, owner, name):
		Utils.err("Settings", "Setting '%s' for class '%s' not found" % (owner, name))
		return None
