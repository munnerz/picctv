import sys
import inspect
import logging
from subprocess import Popen
from tempfile import SpooledTemporaryFile, NamedTemporaryFile

class Settings:

    className = "Settings"

    @staticmethod
    def lookup(a, x, default=lambda x2, y2: Settings.notFound(x2, y2)):
        return a.get(x, default)

    settingMappings = {
                    "Utils":            lambda x, y: Settings.getUtils(x, y),
                    "Capture":          lambda x, y: Settings.getCapture(x, y)
                    }

    utilsSettings = {
                    "showDebug": True,
                    "showError": True,
                    "showInfo": True,
                    "logPath": "./server.log",
                    "mp4TempStoragePath": "/recordings/tmp/"
    }

    captureSettings = {
                    "serverPort": 8000,
                    "serverIp": "0.0.0.0",
                    "chunkSize": 22,
    }

    @staticmethod
    def get(name, owner):
        toExec = Settings.lookup(Settings.settingMappings, owner)
        if(toExec != None):
            return toExec(owner, name)

    @staticmethod
    def getUtils(owner, name):
        m = Settings.lookup(Settings.utilsSettings, name, None)
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
    def notFound(owner, name):
        #Utils.err(Settings.className, "Setting '%s' for class '%s' not found" % (owner, name))
        return None

class Utils:
    className = "Utils"
    file_out = open(Settings.get("logPath", className), "w")

    LOGGER = logging.getLogger(name="server")
    LOGGER.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    LOGGER.addHandler(ch)

    def signal_handler(s, signal):
        Utils.dbg("Signal received", Utils.className)
        Utils.closeFile()
        sys.exit()

    @staticmethod
    def msg(text, sender=None):
        if sender is None:
            callingframe = inspect.currentframe().f_back
            sender = "server.%s" % (callingframe.f_locals['self'].__class__.__name__)
        logging.getLogger("server.%s" % sender).info(text)

    @staticmethod
    def err(text, sender=None):
        if sender is None:
            callingframe = inspect.currentframe().f_back
            sender = "server.%s" % (callingframe.f_locals['self'].__class__.__name__)
        logging.getLogger("server.%s" % sender).error(text)

    @staticmethod
    def dbg(text, sender=None):
        if sender is None:
            callingframe = inspect.currentframe().f_back
            sender = "server.%s" % (callingframe.f_locals['self'].__class__.__name__)
        logging.getLogger("server.%s" % sender).debug(text)

    @staticmethod
    def weblog(text, level, sender=None):
        if sender is None:
            callingframe = inspect.currentframe().f_back
            sender = "server.%s" % (callingframe.f_locals['self'].__class__.__name__)
            library
        from library import log
        log(text, level, sender)

    @staticmethod
    def closeFile():
        Utils.dbg("Closing log file...", Utils.className)
        Utils.file_out.close()

    @staticmethod
    def h264ToMP4(_in):
        _outFile = NamedTemporaryFile(dir="/recordings/tmp/")
        _inFile = SpooledTemporaryFile()
        while True:
            data = _in.read(4096)
            if not data:
                break
            _inFile.write(data)

        Utils.dbg("%d bytes going into ffmpeg" % _inFile.tell(), Utils.className)

        _inFile.seek(0)

        with Popen(["/usr/local/bin/ffmpeg", "-y", "-an", "-i", "-", "-vcodec", "copy", "-movflags", "faststart", "-f", "mp4", _outFile.name], 
            stdin=_inFile) as p:
            p.wait()
            _inFile.close()
            Utils.dbg("Finished creating MP4...", Utils.className)
            return _outFile

        return None

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def get_git_revision_short_hash():
        import subprocess
        return subprocess.check_output(['git', 'describe'])
