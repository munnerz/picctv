## Node settings
NODE_NAME = "Kitchen" # the name of this camera to report to the server - should be unique!

_RECORDING_QUALITIES =   { 
                            "low": { 
                                "format": "yuv", 
                                "resolution": (256, 128),
                                "fps": 5,
                                "multiplexer": None,
                                "splitter_port": 1,
                                "registered_modules": [],
                                "extra_params": {},
                            },

                            "high": {
                                "format": "h264",
                                "resolution": (1280, 720),
                                "fps": 25,
                                "multiplexer": None,
                                "splitter_port": 2,
                                "registered_modules": [],
                                "extra_params": {"quality": 25},
                            },
                        }

ENABLED_MODULES = {
                    "Recording": {
                        "inputs": [
                            ("PiCamera", "high"),
                        ],
                        "arguments": {
                            "chunk_length": 4,
                        },
                    },
                    "Live": {
                        "inputs": [
                            ("PiCamera", "high"),
                        ],
                        "arguments": {
                            "listen_address": ('0.0.0.0', 8000),
                        },
                    },
                    "Motion": {
                        "inputs": [
                            ("BackgroundExtraction", "all"),
                            ("PiCamera", "low"),
                        ],
                        "arguments": {
                            "resolution": _RECORDING_QUALITIES["low"]["resolution"],
                            "level": 750,
                            "threshold": 35,
                            "tmp_file": '/run/shm/picamtemp.dat',
                            "chunk_length": 20,
                            "pixel_change_threshold_scale_factor": 3.5,
                        },
                    },
                    "PiCamera": {
                        "inputs": [
                            ("Motion", "all"),
                        ],
                        "arguments": {
                            "resolution": (1280, 720),
                            "fps": 25,
                            "exposure_mode": 'auto',
                            "brightness": 65,
                            "hflip": True,
                            "vflip": True,
                            "recording_qualities": _RECORDING_QUALITIES,
                        },
                    },
                    "Networking": {
                        "inputs": [
                            ("Recording", "all"),
                            ("Buffer", "Motion:all"),
                        ],
                        "arguments": {
                            "node_name": NODE_NAME,
                            "server_address": ('cctv.lan', 8000),
                        },
                    },
                    "Buffer": {
                        "inputs": [
                            ("Motion", "all"),
                        ],
                        "arguments": {
                            "buffer_size": 30,
                        },
                    },
                    "BackgroundExtraction": {
                        "inputs": [
                            ("PiCamera", "low"),
                        ],
                        "arguments": {
                            "resolution": _RECORDING_QUALITIES["low"]["resolution"],
                            "frame_count_threshold": 20,
                            "tmp_file": '/run/shm/picamtemp_bg.dat',
                        },
                    },
                }

# set up the Python logging module
import logging
LOGGER = logging.getLogger(name="node")
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)

def logger(name):
    return logging.getLogger(name)
# end logging module stuff
