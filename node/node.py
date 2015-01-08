import modules
from networking import Networking
import math, time
import picamera

CAMERA_NAME = "ChangeMe"

_CAMERA = picamera.PiCamera()
_CAMERA.resolution = (1280, 720)
_CAMERA.framerate = 24
_CAMERA.rotation = 270

_MODULES = [modules.Recording(), modules.Live(), modules.Motion()]
_NETWORK = Networking.Networking(CAMERA_NAME)

class Multiplexer(object):
    ''' Multiplexes one video stream out to many modules '''

    def __init__(self):
        self._settings = None

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

        if self._usefulFrame(frame_info.index):
            for module in self._settings['registered_modules'][:]:
                output = module.process_frame((frame, frame_info))
                if output is not None:
                    _NETWORK.send_data((module.get_name(), output))

        return len(frame)

    def flush(self):
        return # modules can't really be flushed...

_recordingQualities =   { 
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
                                #"keyFrameCallback": lambda x: keyFrameDiscovered(x),
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
        print ("Error attempting to unregister module - module not registered.")
        pass


for module in _MODULES:
    _recordingQualities[module.required_quality()]['registered_modules'].append(module)
    print("Added %s module to %s quality multiplexer..." % (module.get_name(), module.required_quality()))

for quality in _recordingQualities:
    profile = _recordingQualities[quality]
    profile['multiplexer'].set_settings(profile)

    print("Starting %s quality recording at %s, FPS: %d, format: %s" % (quality, profile['resolution'], profile['fps'], profile['format']))
    _CAMERA.start_recording(profile['multiplexer'], profile['format'], 
                            profile['resolution'], profile['splitter_port'])


try:
    while True: #main process loop
        time.sleep(1)
except KeyboardInterrupt:
        #shut down all modules here
        map(lambda q: _CAMERA.stop_recording(splitter_port=q['splitter_port']), _recordingQualities.values())
        map(lambda m: shutdown_module(m), _MODULES)
        _NETWORK.shutdown()

        print("Shut down.")
