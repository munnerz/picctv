import threading
import time

from library import library
from utils import Utils

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, asynchronous

class RootHandler(RequestHandler):

	@asynchronous
	def get(self):
		Utils.dbg(__class__.__name__, "Processing incoming connection")
		cameras = library.lib.getCameras()
		Utils.dbg(__class__.__name__, "Cameras: %s" % cameras)
		self.render("templates/home.html", title="PiCCTV Control", cameras=cameras)

class CameraClipList(RequestHandler):
	@asynchronous
	def get(self, cameraId):
		Utils.dbg(__class__.__name__, "Processing incoming request")
		videos = library.lib.getVideos(cameraId)
		self.render("templates/cameraClipList.html", cameraId=cameraId, clips=videos)

class ClipHandler(RequestHandler):
	@asynchronous
	def get(self, clipId):
		Utils.dbg(__class__.__name__, "Processing incoming connection")
		clips = library.lib.getVideo(clipId)
		clip = clips[0]
		nextClip = clips[1] #TODO: catch index out of bounds
		self.render("templates/clipinfo.html", clip=clip, clip_id=clipId, nextClip=nextClip)

class ClipDownloader(RequestHandler):
	@asynchronous
	def get(self, clipId):
		Utils.dbg(__class__.__name__, "Processing incoming connection, clipId=%s" % clipId)
		videoObject = library.lib.getVideo(clipId)[0]
		toSend = Utils.h264ToMP4(videoObject)
		self.set_header("Content-Type", 'video/mp4; charset="utf-8"')
		self.set_header("Content-Disposition", "attachment; filename=%s.mp4" % videoObject.filename)

		while True:
			data = toSend.read(4096)
			if not data: break
			written = self.write(data)
			self.flush()
		self.finish()
		toSend.close()
		Utils.dbg(__class__.__name__, "File sent, clipId=%s" % clipId)

class WebServer(threading.Thread):

	def run(self):
		IOLoop.current().start()

	def make_app(self):
	    return Application([
	    	url(r"/camera/(.*?)/?", CameraClipList),
	    	url(r"/clip/(.*?)/download/?", ClipDownloader),
	    	url(r"/clip/(.*?)/?", ClipHandler),
			url(r"/?", RootHandler),
	        ])

	def __init__(self, library):
		threading.Thread.__init__(self)
		Utils.msg(__class__.__name__, "Starting WebServer...")
		app = self.make_app()
		app.listen(8888)
		Utils.msg(__class__.__name__, "Started WebServer...")

