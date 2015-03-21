from datetime import datetime

import numpy as np
import cv2

import settings

LOGGER = settings.logger("node.modules.OpenCV")
arguments = None

_frames = []


def _storeFrame(frame):
    global _frames
    _frames.insert(0, frame)
    if len(_frames) > arguments['frame_limit']:
        _frames.pop(len(_frames) - 1)

def diff_img():
    global _frames
    if len(_frames) < 3:
        return None
    d1 = cv2.absdiff(_frames[1], _frames[0])
    d2 = cv2.absdiff(_frames[2], _frames[0])
    return cv2.bitwise_and(d1, d2)

def required_quality():
    return "low"

def process_data(data):
    global _frames,arguments
    (module, data) = data
    (frame, frame_info) = data

    res = settings._RECORDING_QUALITIES[required_quality()]['resolution']

    if(len(frame) < res[0] * res[1]):
        print ("Fake frame...")
        return None # we have a fake frame!

    stream = open(arguments['tmp_file'], 'w+b')
    stream.write(frame)
    stream.seek(0)

    np_frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).reshape((res[1], res[0])).astype('float32')

    _storeFrame(np_frame)
    diff = diff_img()

    if diff is None:
        return None

    detected_motion_condition = diff > 6
    detected_motion_pixels = np.extract(detected_motion_condition, diff)

    return {"all": {"time": datetime.now(),
                    "timestamp": frame_info.timestamp,
                    "is_motion": len(detected_motion_pixels) > 0.25 * len(np_frame),
                    "motion_magnitude": len(detected_motion_pixels),
                    "frame_number": frame_info.index}}

def shutdown_module():
    LOGGER.debug("Shut down.")

def name():
    return "OpenCV"