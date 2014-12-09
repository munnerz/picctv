import threading, sys
import modules
import math, time
import picamera
from collections import OrderedDict

class Multiplexer():

	def __init__(self):
		self._settings = None

	def _setSettings(self, settings):
		self._settings = settings

	def _frameInfo(self):
		global _camera
		if self._settings is None: # not ready yet...
			return None
		try:
			return _camera._encoders[self._settings['splitter_port']].frame
		except AttributeError:
			pass
		except IndexError:
			pass
		return None

	def _usefulFrame(self, index):
		global _camera
		if self._settings['fps'] >= _camera.framerate:
			return True
		if index % math.trunc(1 / (self._settings['fps'] / _camera.framerate)) == 0:
			return True
		return False

	def write(self, frame):
		if self._settings is None: #not ready yet...
			return None

		frameInfo = self._frameInfo()

		if frameInfo is None:
			return None

		if self._usefulFrame(frameInfo.index):
			for module in self._settings['registered_modules'][:]:
				module._addFrameToStack(frame, frameInfo)
			return None

	def flush(self):
		return # modules can't really be flushed...

def shutdownModule(module):
	try:
		module.shutdown()
	except NotImplementedError as e:
		print ("Error shutting down module: %s" % e)
		pass

def unregisterModule(module):
	try:
		_modules.remove(module)
	except IndexError:
		print ("Error attempting to unregister module - module not registered.")
		pass


_camera = picamera.PiCamera()
_camera.resolution = (1280, 720)
_camera.framerate = 24

_modules = [ modules.Recording(), modules.Live(), modules.Motion() ]
_recordingQualities = 	{ 
							"low": { 
								"format": "yuv", 
								"resolution": (128, 64),
								"fps": 8,
								"multiplexer": Multiplexer(),
								"splitter_port": 1,
								"registered_modules": [],
							},

							"high": {
								"format": "h264",
								"resolution": (1280, 720),
								"fps": 24,
								"multiplexer": Multiplexer(),
								"splitter_port": 2,
								"registered_modules": [],
							},
						}



for module in _modules:
	_recordingQualities[module.requiredQuality()]['registered_modules'].append(module)
	print ("Added %s module to %s quality multiplexer..." % (module.getName(), module.requiredQuality()))

for quality in _recordingQualities:
	profile = _recordingQualities[quality]
	profile['multiplexer']._setSettings(profile)

	print ("Starting %s quality recording at %s, FPS: %d, format: %s" % (quality, profile['resolution'], profile['fps'], profile['format']))
	_camera.start_recording(profile['multiplexer'], profile['format'], 
							profile['resolution'], profile['splitter_port'])


try:
	while True: #main process loop
		time.sleep(5)
except KeyboardInterrupt:
		#shut down all modules here
		print ("Shutting down modules...")
		for module in _modules[:]:
			shutdownModule(module)
			unregisterModule(module)
