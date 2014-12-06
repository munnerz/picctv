import threading
import time
from io import BytesIO

from library import library
from utils import Utils

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url, asynchronous, StaticFileHandler

APP_NAME = "PiCCTV" #TODO: Load this more gracefully

class RootHandler(RequestHandler):

	@asynchronous
	def get(self):
		Utils.dbg(__class__.__name__, "Processing incoming connection")
		cameras = library.lib.getCameras()
		Utils.dbg(__class__.__name__, "Cameras: %s" % cameras)
		self.render("templates/home.html", app_name=APP_NAME, title="PiCCTV Control", cameras=cameras)

class CameraClipList(RequestHandler):
	@asynchronous
	def get(self, cameraId):
		Utils.dbg(__class__.__name__, "Processing incoming request")
		videos = library.lib.getVideos(cameraId)
		self.render("templates/cameraClipList.html", app_name=APP_NAME, cameraId=cameraId, clips=videos)

class ClipHandler(RequestHandler):
	@asynchronous
	def get(self, clipId):
		Utils.dbg(__class__.__name__, "Processing incoming connection")
		clips = library.lib.getVideo(clipId)
		if(len(clips) == 0):
			self.write("Clip not found...")
			self.finish()
		elif(len(clips) == 1):
			nextClip = False
		else:
			nextClip = clips[1]
		clip = clips[0]
		clip.motionEvents = library.lib.numberOfMotionEvents(clipId)
		self.render("templates/clipinfo.html", app_name=APP_NAME, clip=clip, clip_id=clipId, nextClip=nextClip)

class ClipDownloader(StaticFileHandler):
	@classmethod
	def get_content(cls, abspath, start=0, end=None):
		file = library.lib.getVideo(abspath, 1)[0]
		if start is not None:
			file.seek(start)
		if end is not None:
			remaining = end - (start or 0)
		else:
			remaining = None
		while True:
			chunk_size = 64 * 1024
			if remaining is not None and remaining < chunk_size:
				chunk_size = remaining
			chunk = file.read(chunk_size)
			if chunk:
				if remaining is not None:
					remaining -= len(chunk)
				yield chunk
			else:
				if remaining is not None:
					assert remaining == 0
				return

	def get_content_size(self):
		videoObject = library.lib.getVideo(self.path, 1)[0]
		return videoObject.length

	def get_modified_time(self):
		return None

	@classmethod
	def get_absolute_path(cls, root, path):
		return path

	def validate_absolute_path(self, root, absolute_path):
		try:
			videoObject = library.lib.getVideo(self.path, 1)[0]
			return absolute_path
		except exceptions.IndexException:
			raise HTTPError(404)


class WebServer(threading.Thread):

	def run(self):
		IOLoop.current().start()

	def make_app(self):
		return Application([
			url(r"/camera/(.*?)/?", CameraClipList),
			url(r"/clip/(.*?)/download/?", ClipDownloader, {'path': ""}),
			url(r"/clip/(.*?)/?", ClipHandler),
			url(r"/?", RootHandler),
			])

	def __init__(self, library):
		threading.Thread.__init__(self)
		Utils.msg(__class__.__name__, "Starting WebServer...")
		app = self.make_app()
		app.listen(8888)
		Utils.msg(__class__.__name__, "Started WebServer...")

