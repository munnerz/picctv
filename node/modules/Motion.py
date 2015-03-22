# Description: Performs motion detection on the frames.
#
# Inputs:      BackgroundExtraction, PiCamera (frame, frame_info) tuples
# Output:      {"time": _, # current datetime at the time of this frame
#               "timestamp": _, # timestamp into the current recording
#               "is_motion": _, # whether or not motion has been triggered
#               "motion_magnitude": _, # the calculated amount motion pixels
#               "frame_number": _} # the frame number in this recording


from datetime import datetime
from collections import Counter

import numpy as np
import cv2

from node import settings

LOGGER = settings.logger("node.modules.Motion")

#initialise both of these to matrices of zeros
_background_model = None

_first_diff_abs = None
_rapid_matching_candidates = None
_stable_signal_candidates = None
_accurate_matching_candidates = None

_long_variance = None
_short_variance = None

def process_data(data):
    global process_frame, _first_diff_abs, _short_variance, _long_variance, _background_model

    (module, data) = data

    if module[0] == "BackgroundExtraction":
        _background_model = data
        return None

    if _background_model is None:
        LOGGER.debug("Skipping motion detection on this frame as we don't have a background image yet...")
        return None

    (frame, frame_info) = data

    if frame_info.index < 50:
        #let's wait...
        return None

    res = arguments['resolution']

    if(len(frame) < res[0] * res[1]):
        LOGGER.error("Fake frame... (len: %d, expected: %d)" % (len(frame), res[0]*res[1]))
        return None # we have a fake frame!

    stream = open(arguments['tmp_file'], 'w+b')
    stream.write(frame)
    stream.seek(0)

    np_frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).reshape((res[1], res[0]))
    
    motion_diff_abs = np.absolute(np.subtract(np_frame, _background_model))

    kernel = np.ones((5,5),np.uint8)
    motion_diff_abs = cv2.erode(motion_diff_abs,kernel,iterations = 1)
    motion_diff_abs = cv2.dilate(motion_diff_abs,np.ones((3,3),np.uint8),iterations = 2)

    if _first_diff_abs is None:
        _first_diff_abs = motion_diff_abs # this should possibly be the second abs diff,
                                               # as this first will be all zeroes

    # now, as per B. alarms trigger module, we should split the image into w x w blocks,
    # take the average grey of them, and work with that

    if _short_variance is None:
        _short_variance = _first_diff_abs

    N = 3.5

    _short_variance_gt_mask = ~(np.greater(N * motion_diff_abs, _short_variance))
    _short_variance_lt_mask = ~(np.less(N * motion_diff_abs, _short_variance))

    t = np.ma.array(_short_variance, mask=_short_variance_gt_mask, copy=False)
    t += 2

    t = np.ma.array(_short_variance, mask=_short_variance_lt_mask, copy=False)
    t -= 1


    if _long_variance is None:
        _long_variance = _first_diff_abs

    # these are sort of swapped, as an efficiency improvement.
    # masks are represented inverted (ie. True values ARE masked), we need
    # to invert the result to make values we WANT, be False. This is it:
    _long_variance_gt_mask = np.less(_short_variance, _long_variance)
    _long_variance_lt_mask = np.greater(_short_variance, _long_variance)

    t = np.ma.array(_long_variance, mask=_long_variance_gt_mask, copy=False)
    t += 2

    t = np.ma.array(_long_variance, mask=_long_variance_lt_mask, copy=False)
    t -= 1

    _best_variance = N * np.minimum(_long_variance, _short_variance)

    _binary_motion_detection_mask = motion_diff_abs > _best_variance

    _motion_detected_pixels = len(np.extract(_binary_motion_detection_mask, _binary_motion_detection_mask))

    return {"all": {"time": datetime.now(),
                    "timestamp": frame_info.timestamp,
                    "is_motion": _motion_detected_pixels > arguments['level'],
                    "motion_magnitude": _motion_detected_pixels,
                    "frame_number": frame_info.index},
            "diff": motion_diff_abs,
            "mask": _binary_motion_detection_mask.astype('float32'),
            "short_variance": _short_variance,
            "long_variance": _long_variance}


def name():
    return "Motion"
    
def shutdown_module():
    LOGGER.debug("Shut down.")
