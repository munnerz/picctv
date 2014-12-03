from io import BytesIO
import threading
import picamera
import stream
from utils import Utils, Settings

class Multiplexer:
	def __init__(self):
		self.outputs = []
		self.lock = threading.Lock()
		print ("started")

	def close(self):
		with self.lock:
			for output in self.outputs:
				try:
					output.close()
					self.outputs.remove(output)
				except Exception as e:
					Utils.err(self.__class__.__name__, "Exception whilst writing to output: %s" % e)
					pass

	def addOutput(self, outputs):
		print ("adding an output")
		with self.lock:
			if isinstance(outputs, list):
				for output in outputs:
					print ("added another")
					self.outputs.append(output)

			else:
				self.outputs.append(outputs)

	def removeOutput(self, outputs):
		with self.lock:
			if isinstance(outputs, list):
				for output in o:
					self.outputs.remove(output)
			else:
				self.outputs.remove(outputs)

	def getOutputs(self):
		with self.lock:
			return list(self.outputs)

	def flush(self):
		print ("flushing")
		num = 0
		with self.lock:
			for output in self.outputs:
				try:
					num = output.flush()
				except Exception as e:
					Utils.err(self.__class__.__name__, "Exception whilst flushing output: %s" % e)
					self.removeOutput(output)
					pass
		return num

	def write(self, data):
		print ("writing")
		with self.lock:
			sendTo = list(self.outputs)
		for output in sendTo:
			try:
				output.write(data)
			except Exception as e:
				Utils.err(self.__class__.__name__, "Exception whilst writing to output: %s" % e)
				self.removeOutput(output)
				pass
		return None

	def __getattr__(self, attr):
		print ("Not implemented: %s" % attr)
		return None

class Capture():

	def __init__(self, networkManager, camera, _format='h264'):
		self.thread = threading.Thread(target=self.run)
		self._format = _format
		self._networkManager = networkManager
		self._camera = camera
		
		self._chunk_length = Settings.get(self.__class__.__name__, "chunkLength")
		self._keepRecording = True
		self._multiplexer = Multiplexer()
		self._streamServer = stream.StreamServer(self._multiplexer)

		self._streamServer.start()
		self.thread.start()

	def run(self):
		Utils.msg(self.__class__.__name__, "Starting capturing...")
		try:
			vidOut = self._networkManager.connection()
			vidOutFO = vidOut.fileObject()
			oldVidOut = None
			self._camera.start_recording(self._multiplexer, self._format, (1280, 720), quality=25)
			self._multiplexer.addOutput(vidOutFO)
			while self.keepRecording():
				try:
					Utils.dbg(self.__class__.__name__, "Waiting for %d seconds" % self._chunk_length)
					self._camera.wait_recording(self._chunk_length)

					Utils.dbg(self.__class__.__name__, "Splitting recording...")
					oldVidOut = vidOut
					nextVidOut = self._networkManager.connection()	
					nextVidOutFO = nextVidOut.fileObject()				
					nextMultiplexer = Multiplexer()
					self._streamServer.multiplexer = nextMultiplexer
					nextMultiplexer.addOutput(self._multiplexer.outputs)
					nextMultiplexer.removeOutput(vidOutFO)
					nextMultiplexer.addOutput(nextVidOutFO)
					self._multiplexer = nextMultiplexer
					self._camera.split_recording(self._multiplexer)
					Utils.dbg(self.__class__.__name__, "Recording split!")

					vidOut = nextVidOut
					vidOutFO = nextVidOutFO
				except picamera.exc.PiCameraRuntimeError as e:
					Utils.err(self.__class__.__name__, "PiCamera runtime error: %s" % e)
					raise
					break
				except Exception as e:
					Utils.err(self.__class__.__name__, "Unhandled exception in recording loop %s" % e)
					pass
					break
				finally:
					if(oldVidOut != None):
						Utils.dbg(self.__class__.__name__, "Closing old vidout")
						oldVidOut.close()
						oldVidOut = None
		except Exception as e:
			Utils.err(self.__class__.__name__, "Capturing failed, exception: %s" % e)
			raise
		finally:
			try:
				Utils.dbg(self.__class__.__name__, "Stopping recording")
				self._camera.stop_recording()
			except Exception as e:
				Utils.err(self.__class__.__name__, "Unhandled exception closing camera, continuing anyway... Exception: %s" % e)
				raise
		self.thread = threading.Thread(target=self.run)
		self.thread.start()


	def keepRecording(self):
		return self._keepRecording

	def stop(self):
		Utils.msg(self.__class__.__name__, "Stopping...")
		self._camera.stop_recording()
		Utils.msg(self.__class__.__name__, "Stopped...")
