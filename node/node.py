import logging
import math
import time

import picamera

import settings
from settings import _RECORDING_QUALITIES
from networking import Networking


LOGGER = logging.getLogger(name="node")
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)

class Multiplexer(object):
    ''' Multiplexes one video stream out to many modules '''

    def __init__(self, _settings=None):
        self._settings = _settings
        self._frame_buffer = ''

    def _frame_info(self):
        if self._settings is None: # not ready yet...
            return None
        try:
            return _CAMERA._encoders[self._settings['splitter_port']].frame
        except AttributeError:
            pass
        except IndexError:
            pass
        return None

    def _usefulFrame(self, index):
        if self._settings['format'] == 'h264':
            return True #all h264 frames are needed for a valid h264 stream

        if self._settings['fps'] >= _CAMERA.framerate:
            return True
        if index % math.trunc(1 / (self._settings['fps'] / _CAMERA.framerate)) == 0:
            return True
        return False

    def write(self, frame):
        if self._settings is None: #not ready yet...
            return None

        frame_info = self._frame_info()

        if frame_info is None:
            return None

        self._frame_buffer = b''.join([self._frame_buffer, frame])

        if frame_info.complete:
            if self._usefulFrame(frame_info.index):
                for module in self._settings['registered_modules'][:]:
                    try:
                        output = module.process_frame((self._frame_buffer, frame_info))
                        if output is not None:
                            _NETWORK.send_data((module.name(), output))
                    except Exception as e:
                        LOGGER.exception("Exception in Multiplexer for module '%s': %s" % (module, e))
                        pass
            self._frame_buffer = b''

        return len(frame)

    def flush(self):
        return # modules can't really be flushed...

def shutdown_module(module):
    try:
        module.shutdown()
    except NotImplementedError as e:
        print("Error shutting down module: %s" % e)
        pass

if __name__ == "__main__":
    _CAMERA = picamera.PiCamera()
    _CAMERA.resolution = settings.CAMERA_RESOLUTION
    _CAMERA.framerate = settings.CAMERA_FPS
    _CAMERA.exposure_mode = settings.CAMERA_EXPOSURE_MODE
    _CAMERA.brightness = settings.CAMERA_BRIGHTNESS
    _CAMERA.hflip = settings.CAMERA_HFLIP
    _CAMERA.vflip = settings.CAMERA_VFLIP

    from importlib import import_module
    _MODULES = map(lambda x: import_module("modules.%s" % x), settings.ENABLED_MODULES)

    _NETWORK = Networking.Networking(settings.NODE_NAME)
    
    for module in _MODULES:
        LOGGER.info("Starting %s" % module.__name__)
        _RECORDING_QUALITIES[module.required_quality()]['registered_modules'].append(module)
        LOGGER.info("Added %s module to %s quality multiplexer..." % (module.__name__, module.required_quality()))

    for quality in _RECORDING_QUALITIES:
        profile = _RECORDING_QUALITIES[quality]
	profile['multiplexer'] = Multiplexer(profile)

        LOGGER.info("Starting %s quality recording at %s, FPS: %d, format: %s" % (quality, profile['resolution'], profile['fps'], profile['format']))
        _CAMERA.start_recording(profile['multiplexer'], profile['format'], 
                                profile['resolution'], profile['splitter_port'], **profile['extra_params'])


    try:
        while True: #main process loop
            time.sleep(1)
    except KeyboardInterrupt:
            #shut down all modules here
            map(lambda q: _CAMERA.stop_recording(splitter_port=q['splitter_port']), _RECORDING_QUALITIES.values())
            _NETWORK.shutdown()
            map(lambda m: shutdown_module(m), _MODULES)

            LOGGER.info("Shut down.")
