import sys
import inspect
import threading
import picamera

 
piCam = None
cameraInitLock = threading.Lock()

class Utils:

	className = "Utils"

	@staticmethod
	def getPiCamera():
		global piCam, cameraInitLock
		if piCam == None:
			Utils.dbg(Utils.className, "Construction PiCam")
			cameraInitLock.acquire()
			piCam = picamera.PiCamera()
			Utils.configurePiCamera(piCam)
			cameraInitLock.release()
		return piCam

	@staticmethod
	def configurePiCamera(piCam): #TODO: Make these load from file
		piCam.resolution = (1280, 720)
		piCam.annotate_background = True 
		piCam.framerate = 24
		piCam.iso = 0
		piCam.brightness = 60
		piCam.exposure_mode = 'night'
		piCam.vflip = False
		piCam.hflip = True

	@staticmethod
	def signal_handler(s, signal):
		Utils.dbg(Utils.className, "Signal received")
		sys.exit()

	@staticmethod
	def msg(sender, text):
		print ("[%s] INFO: %s" % (sender, text))

	@staticmethod
	def err(sender, text, quit=False):
		print ("[%s] ERROR: %s" % (sender, text))
		if quit:
			Utils.err(Utils.className, "Err quit functionality not added yet", False)

	@staticmethod
	def dbg(sender, text):
		if Settings.get(Utils.className, "showDebug"):
			print ("[%s] DEBUG: %s" % (sender, text))

	@staticmethod
	def dbg2(sender, text):
		if Settings.get(Utils.className, "showDebug2"):
			print ("[%s] DEBUG2: %s" % (sender, text))

class Settings:

	@staticmethod
	def lookup(a, x, default=lambda x2, y2: Settings.notFound(x2, y2)):
		return a.get(x, default)

	settingMappings = {
					"NetworkManager": 	lambda x, y: Settings.getNetworkManager(x, y),
				 	"Capture":			lambda x, y: Settings.getCapture(x, y),
				 	"Utils":			lambda x, y: Settings.getUtils(x, y),
				 	"NetworkConnection":lambda x, y: Settings.getNetworkConnection(x, y),
				 	"Analysis":			lambda x, y: Settings.getAnalysis(x, y),
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

	analysisSettings = {
					"splitterPort": 2,
	}

	@staticmethod
	def get(owner, name):
		toExec = Settings.lookup(Settings.settingMappings, owner)
		if(toExec != None):
			return toExec(owner, name)

	@staticmethod
	def getNetworkManager(owner, name):
		m = Settings.lookup(Settings.networkManagerSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@staticmethod
	def getCapture(owner, name):
		m = Settings.lookup(Settings.captureSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@staticmethod
	def getUtils(owner, name):
		m = Settings.lookup(Settings.utilsSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@staticmethod
	def getNetworkConnection(owner, name):
		m = Settings.lookup(Settings.networkConnectionSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@staticmethod
	def getAnalysis(owner, name):
		m = Settings.lookup(Settings.analysisSettings, name, None)
		if m == None:
			return Settings.notFound(owner, name)
		return m

	@staticmethod
	def notFound(owner, name):
		Utils.err("Settings", "Setting '%s' for class '%s' not found" % (owner, name))
		return None
