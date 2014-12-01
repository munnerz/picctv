import sys
import inspect

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

	def lookup(a, x, default=lambda x2, y2: Settings.notFound(x2, y2)):
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
					"showDebug": False,
					"showError": True,
					"showInfo": True,
	}

	networkConnectionSettings = {
					"cameraId": "Front Door",
	}

	def get(owner, name):
		toExec = Settings.lookup(Settings.settingMappings, owner)
		if(toExec != None):
			return toExec(owner, name)



	def getNetworkManager(owner, name):
		m = Settings.lookup(Settings.networkManagerSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	def getCapture(owner, name):
		m = Settings.lookup(Settings.captureSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	def getUtils(owner, name):
		m = Settings.lookup(Settings.utilsSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	def getNetworkConnection(owner, name):
		m = Settings.lookup(Settings.networkConnectionSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m


	def notFound(owner, name):
		Utils.err("Settings", "Setting '%s' for class '%s' not found" % (owner, name))
		return None
