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
					"logPath": "/recordings/log/server.log",
					"mp4TempStoragePath": "/recordings/tmp/"
	}

	captureSettings = {
					"serverPort": 8000,
					"serverIp": "0.0.0.0",
					"chunkSize": 22,
	}

	webServerSettings = {

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
		_outFile = NamedTemporaryFile(dir="/recordings/tmp/")
		_inFile = SpooledTemporaryFile()
		while True:
			data = _in.read(4096)
			if not data:
				break
			_inFile.write(data)

		Utils.dbg(Utils.className, "%d bytes going into ffmpeg" % _inFile.tell())

		_inFile.seek(0)

		with Popen(["/usr/local/bin/ffmpeg", "-y", "-an", "-i", "-", "-vcodec", "copy", "-movflags", "faststart", "-f", "mp4", _outFile.name], 
			stdin=_inFile) as p:
			p.wait()
			_inFile.close()
			Utils.dbg(Utils.className, "Finished creating MP4...")
			return _outFile

		return None

	def sizeof_fmt(num, suffix='B'):
		for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
			if abs(num) < 1024.0:
				return "%3.1f%s%s" % (num, unit, suffix)
			num /= 1024.0
		return "%.1f%s%s" % (num, 'Yi', suffix)

	def get_git_revision_short_hash():
		import subprocess
		return subprocess.check_output(['git', 'describe'])