# Description: This module reads data from the PiCamera, at various configured qualities,
#              and sends its output as a (frame, frame_info) tuple (where frame_info is a
#              PiVideoFrame object.
#
# Inputs:      None
# Output:      (frame, frame_info)

import picamera
import math
from node import settings

arguments = None
_output_queues = None

LOGGER = settings.logger("node.modules.PiCamera")
_CAMERA = None
flags = {}

class Multiplexer(object):
    ''' Multiplexes one video stream out to many modules '''

    def __init__(self, _quality, _settings=None):
        self._quality = _quality
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

    def _useful_frame(self, index):
        if self._settings['format'] == 'h264':
            return True #all h264 frames are needed for a valid h264 stream

        if self._settings['fps'] >= _CAMERA.framerate:
            return True
        if index % math.trunc(1 / (self._settings['fps'] / _CAMERA.framerate)) == 0:
            return True
        return False

    def write(self, frame):
        try:
            if self._settings is None: #not ready yet...
                return None

            frame_info = self._frame_info()
            self._frame_buffer = b''.join([self._frame_buffer, frame])
            
            if frame_info is None:
                return None

            if frame_info.index < 40:
                return None

            if frame_info.index % 15000 == 0:
                LOGGER.debug("Enabling auto exposure")
                _CAMERA.exposure_mode = 'auto'

            if (frame_info.index - 125) % 15000 == 0:
                LOGGER.debug("Turning off auto exposure")
                _CAMERA.exposure_mode = 'off'

            if frame_info.complete:
                if self._useful_frame(frame_info.index):
                    global _output_queues
                    map(lambda x: x.put( ( ("PiCamera", self._quality), (self._frame_buffer, frame_info) )), _output_queues[self._quality])
                self._frame_buffer = b''

            return len(frame)
        except Exception as e:
            LOGGER.error("Exception in Multiplexer for quality %s. Exception: %s." % (self._quality, e))

    def flush(self):
        return # modules can't really be flushed...

def process_data(data):
    global _CAMERA, flags
    (module, data) = data

    flags[module[0]] = data['is_motion']

    display = "%d: " % (arguments['recording_qualities']['low']['multiplexer']._frame_info().index)
    for m, n in flags.items():
        display += "%s: %s, " % (m, n)
    display = display[0:-2]

    _CAMERA.annotate_text = display

    return None

def module_started():
    global _CAMERA, arguments
    _CAMERA = picamera.PiCamera()
    _CAMERA.resolution = arguments['resolution']
    _CAMERA.framerate = arguments['fps']
    _CAMERA.exposure_mode = arguments['exposure_mode']
    _CAMERA.brightness = arguments['brightness']
    _CAMERA.hflip = arguments['hflip']
    _CAMERA.vflip = arguments['vflip']
    _CAMERA.awb_mode = 'off'
    _CAMERA.awb_gains = 1.4
    _CAMERA.annotate_background = True

    for quality, profile in arguments['recording_qualities'].items():
        profile['multiplexer'] = Multiplexer(quality, profile)

        LOGGER.info("Starting %s quality recording at %s, FPS: %d, format: %s" % (quality, profile['resolution'], profile['fps'], profile['format']))
        _CAMERA.start_recording(profile['multiplexer'], profile['format'],
                                profile['resolution'], profile['splitter_port'], **profile['extra_params'])


def name():
    return "PiCamera"

def shutdown_module():
    global _CAMERA, arguments
    map(lambda q: _CAMERA.stop_recording(splitter_port=q['splitter_port']), arguments['recording_qualities'].values())
    _CAMERA.close()

