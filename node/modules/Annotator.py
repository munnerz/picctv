# This module accepts updates the PiCamera annotate field to annotate
# the H264 video stream as it's being encoded

import picamera

_CAMERA = None
flags = {}

def start_module():
	global _CAMERA
	_CAMERA = picamera.PiCamera()

def process_data(data):
	(module, data) = data

	if module[0] != "Motion":
		LOGGER.error("Invalid input. Annotator only accepts Motion data.")

	flags[module[0]] = data['is_motion']

	display = ""
	for m, n in flags.items():
		display += "%s: %n, "
	display = display[0:-2]

	return None