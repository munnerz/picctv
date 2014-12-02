from io import BytesIO
import threading
import picamera
from utils import Utils, Settings


class Capture():

	def __init__(self, networkManager, _format='h264'):
		self.thread = threading.Thread(target=self.run)
		self._format = _format
		self._networkManager = networkManager

		self._chunk_length = Settings.get(self.__class__.__name__, "chunkLength")
		self._keepRecording = True

		self.thread.start()

	def run(self):
		Utils.msg(self.__class__.__name__, "Starting capturing...")
		rerun = False
		try:
			vidOut = self._networkManager.connection()
			oldVidOut = None
			Utils.getPiCamera().start_recording(vidOut.fileObject(), self._format, quality=25)
			while self.keepRecording():
				try:
					Utils.dbg(self.__class__.__name__, "Waiting for %d seconds" % self._chunk_length)
					Utils.getPiCamera().wait_recording(self._chunk_length)
					nextVidOut = self._networkManager.connection()
					Utils.dbg(self.__class__.__name__, "Splitting recording...")
					oldVidOut = vidOut
					Utils.getPiCamera().split_recording(nextVidOut.fileObject())
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
				Utils.getPiCamera().stop_recording()
			except Exception as e:
				Utils.err(self.__class__.__name__, "Unhandled exception closing camera, continuing anyway... Exception: %s" % e)
				pass
		self.thread = threading.Thread(target=self.run)
		self.thread.start()


	def keepRecording(self):
		return self._keepRecording

	def stop(self):
		Utils.msg(self.__class__.__name__, "Stopping...")
		Utils.getPiCamera().stop_recording()
		Utils.msg(self.__class__.__name__, "Stopped...")
