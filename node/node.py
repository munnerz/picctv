import logging
import math
import time

import picamera

import modules
from networking import Networking


LOGGER = logging.getLogger(name="node")
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)



CAMERA_NAME = "ChangeMe"

_CAMERA = picamera.PiCamera()
_CAMERA.resolution = (1280, 720)
_CAMERA.framerate = 24
_CAMERA.exposure_mode = 'night'
_CAMERA.brightness = 60

_MODULES = [modules.Recording(), modules.Live(), modules.Motion()]
_NETWORK = Networking.Networking(CAMERA_NAME)

class Multiplexer(object):
    ''' Multiplexes one video stream out to many modules '''

    def __init__(self):
        self._settings = None
        self._frame_buffer = ''

    def set_settings(self, settings):
        self._settings = settings

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
                            _NETWORK.send_data((module.get_name(), output))
                    except Exception as e:
                        LOGGER.exception("Exception in Multiplexer for module '%s': %s" % (module, e))
                        pass
            self._frame_buffer = b''

        return len(frame)

    def flush(self):
        return # modules can't really be flushed...

_recordingQualities =   { 
                            "low": { 
                                "format": "yuv", 
                                "resolution": (64, 128),
                                "fps": 8,
                                "multiplexer": Multiplexer(),
                                "splitter_port": 1,
                                "registered_modules": [],
                                "extra_params": {},
                            },

                            "high": {
                                "format": "h264",
                                "resolution": (1280, 720),
                                "fps": 24,
                                "multiplexer": Multiplexer(),
                                "splitter_port": 2,
                                "registered_modules": [],
                                "extra_params": {"quality": 25},
                            },
                        }

def shutdown_module(module):
    try:
        module.shutdown()
    except NotImplementedError as e:
        print("Error shutting down module: %s" % e)
        pass

def unregister_module(module):
    try:
        _MODULES.remove(module)
    except IndexError:
        LOGGER.warning("Error attempting to unregister module - module not registered.")
        pass


for module in _MODULES:
    _recordingQualities[module.required_quality()]['registered_modules'].append(module)
    LOGGER.info("Added %s module to %s quality multiplexer..." % (module.get_name(), module.required_quality()))

for quality in _recordingQualities:
    profile = _recordingQualities[quality]
    profile['multiplexer'].set_settings(profile)

    LOGGER.info("Starting %s quality recording at %s, FPS: %d, format: %s" % (quality, profile['resolution'], profile['fps'], profile['format']))
    _CAMERA.start_recording(profile['multiplexer'], profile['format'], 
                            profile['resolution'], profile['splitter_port'], **profile['extra_params'])


try:
    while True: #main process loop
        time.sleep(1)
except KeyboardInterrupt:
        #shut down all modules here
        map(lambda q: _CAMERA.stop_recording(splitter_port=q['splitter_port']), _recordingQualities.values())
        _NETWORK.shutdown()
        map(lambda m: shutdown_module(m), _MODULES)

        LOGGER.info("Shut down.")
