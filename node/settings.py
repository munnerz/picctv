from modules.Recording import Recording
from modules.Live import Live
from modules.Motion import Motion

## Node settings
NODE_NAME = "ChangeMe" # the name of this camera to report to the server - should be unique!
ENABLED_MODULES = [Recording, Live, Motion]

## Camera settings
CAMERA_RESOLUTION = (1280, 720) # the actual recording resolution used by PiCamera
CAMERA_FPS = 24 #the actual FPS to capture at (everything else is scaled off this...)
CAMERA_EXPOSURE_MODE = 'night' 
CAMERA_BRIGHTNESS = 60 # value between 0 and 100
CAMERA_HFLIP = False
CAMERA_VFLIP = False
_RECORDING_QUALITIES =   { 
                            "low": { 
                                "format": "yuv", 
                                "resolution": (64, 128),
                                "fps": 8,
                                "multiplexer": None,
                                "splitter_port": 1,
                                "registered_modules": [],
                                "extra_params": {},
                            },

                            "high": {
                                "format": "h264",
                                "resolution": (1280, 720),
                                "fps": 24,
                                "multiplexer": None,
                                "splitter_port": 2,
                                "registered_modules": [],
                                "extra_params": {"quality": 25},
                            },
                        }

## Module settings
LIVE_LISTEN_ADDRESS = ('0.0.0.0', 8000) # address for the

RECORDING_CHUNK_LENGTH = 4 # target length of each chunk, in seconds

MOTION_LEVEL = 10000
MOTION_THRESHOLD = 35
MOTION_TMP_FILE = '/run/shm/picamtemp.dat' # this really should be a ramdisk as it'll be read & written
                                           # to very often (twice per frame)
MOTION_CHUNK_LENGTH = 10 # the number of data points to collect before sending to server
MOTION_BACKGROUND_FRAME_COUNT_THRESHOLD = 20 # how many frames we must have processed before starting
                                             # actual analysis.
