from io import BytesIO
import threading
import picamera
from utils import Utils, Settings


class Capture():

	def __init__(self, networkManager, _format='h264', camera = picamera.PiCamera()):
		self.thread = threading.Thread(target=self.run)
		self._camera = camera
		self._format = _format
		self._networkManager = networkManager

		self._chunk_length = Settings.get(__class__.__name__, "chunkLength")
		self._keepRecording = True

		self.configure()

		self.thread.start()

	def configure(self, resolution = (1280, 720), framerate = 24):
		self._camera.resolution = resolution
		self._camera.framerate = framerate
		self._camera.iso = 0
		self._camera.exposure_mode = 'night'
		self._camera.vflip = True
		self._camera.hflip = True #hflip should always be on as the camera captures mirrored

	def run(self):
		Utils.msg(self.__class__.__name__, "Starting capturing...")
		rerun = False
		try:
			vidOut = self._networkManager.connection()
			oldVidOut = None
			self._camera.start_recording(vidOut.fileObject(), self._format, quality=25)
			while self.keepRecording():
				try:
					Utils.dbg(self.__class__.__name__, "Waiting for %d seconds" % self._chunk_length)
					self._camera.wait_recording(self._chunk_length)
					nextVidOut = self._networkManager.connection()
					Utils.dbg(self.__class__.__name__, "Splitting recording...")
					oldVidOut = vidOut
					self._camera.split_recording(nextVidOut.fileObject())
					Utils.dbg(self.__class__.__name__, "Recording split!")
					vidOut = nextVidOut
				except picamera.exc.PiCameraRuntimeError as e:
					Utils.err(self.__class__.__name__, "PiCamera runtime error: %s" % e)
					pass
					break
				except Exception as e:
					Utils.err(self.__class__.__name__, "Unhandled exception in recording loop %s" % e)
					pass
					break
				finally:
					if(oldVidOut != None):
						Utils.dbg(self.__class__.__name__, "Closing old vidout")
						oldVidOut.stop()
						oldVidOut = None
		except Exception as e:
			Utils.err(self.__class__.__name__, "Capturing failed, exception: %s" % e)
			pass
		finally:
			try:
				Utils.dbg(self.__class__.__name__, "Stopping recording")
				self._camera.stop_recording()
			except Exception as e:
				Utils.err(self.__class__.__name__, "Unhandled exception closing camera, continuing anyway... Exception: %s" % e)
				pass
		self.thread = threading.Thread(target=self.run)
		self.thread.start()


	def keepRecording(self):
		return self._keepRecording

	def stop(self):
		Utils.msg(self.__class__.__name__, "Stopping...")
		self._camera.stop_recording()
		Utils.msg(self.__class__.__name__, "Stopped...")
