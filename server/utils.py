import sys
from subprocess import Popen, PIPE
from io import BytesIO
from tempfile import SpooledTemporaryFile, NamedTemporaryFile
import os

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
					"logPath": "/home/james/picctv/server.log"
	}

	captureSettings = {
					"serverPort": 8000,
					"serverIp": "0.0.0.0",
					"chunkSize": 22,
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
		#Utils.err(Settings.className, "Setting '%s' for class '%s' not found" % (owner, name))
		return None

class Utils:
	className = "Utils"
	file_out = open(Settings.get(className, "logPath"), "w")

	def signal_handler(s, signal):
		Utils.dbg(Utils.className, "Signal received")
		Utils.closeFile()
		sys.exit()

	def msg(sender, text):
		t = ("[%s] INFO: %s" % (sender, text))
		Utils.file_out.write("%s\n" % t)
		Utils.file_out.flush()
		if Settings.get(Utils.className, "showInfo"):
			print (t)

	def err(sender, text, quit=False):
		t = ("[%s] ERROR: %s" % (sender, text))
		Utils.file_out.write("%s\n" % t)
		Utils.file_out.flush()
		if Settings.get(Utils.className, "showError"):
			print (t)
		if quit:
			Utils.err(Utils.className, "Err quit functionality not added yet", False)

	def dbg(sender, text):
		t = ("[%s] DEBUG: %s" % (sender, text))
		Utils.file_out.write("%s\n" % t)
		Utils.file_out.flush()
		if Settings.get(Utils.className, "showDebug"):
			print (t)

	def closeFile():
		Utils.dbg(Utils.className, "Closing log file...")
		Utils.file_out.close()

	def h264ToMP4(_in):
		_inFile = SpooledTemporaryFile(50*1024*1024) #TODO: Make this load from config
		while True:
			data = _in.read(4096)
			if not data:
				break
			_inFile.write(data)

		Utils.dbg(Utils.className, "%d bytes going into ffmpeg" % _inFile.tell())

		_inFile.seek(0)
		_outFile = NamedTemporaryFile() 

		p = Popen(["/usr/local/bin/ffmpeg", "-y", "-an", "-i", "-", "-vcodec", "copy", "-movflags", "faststart", "-f", "mp4", _outFile.name], 
			stdin=_inFile)
		p.wait()
		Utils.dbg(Utils.className, "Finished creating MP4...")
		_outFile.seek(0)
		return _outFile
#			output = BytesIO()
#			length = 0
#			while True:
#				data = p.stdout.read(1024)
#				if len(data) == 0:
#					break
#				length += output.write(data)
#				# do something with data...
#			Utils.dbg(Utils.className, "Read %d bytes from ffmpeg" % length)
#			output.seek(0)
#			return output # should have finisted anyway