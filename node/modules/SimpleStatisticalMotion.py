from datetime import datetime

import numpy as np
import cv2

import settings

LOGGER = settings.logger("node.modules.SimpleStatisticalMotion")

#initialise both of these to matrices of zeros
_background_sum = None
_background_sum_squared = None
_background_frame_count = 0 #the number of frames that comprise the background data

_last_timestamp = 0

arguments = None

def _update_background(frame):
    global _background_sum, _background_sum_squared, _background_frame_count
    if _background_sum is None and _background_sum_squared is None:
        _background_sum = frame
        _background_sum_squared = cv2.pow(frame, 2.0)
    else:
        cv2.accumulate(frame, _background_sum)
        cv2.accumulateSquare(frame, _background_sum_squared)
    _background_frame_count += 1

def _background_mean():
    global _background_sum, _background_frame_count
    return _background_sum / _background_frame_count

def _background_variance():
    global _background_sum_squared, _background_frame_count
    squared_sum_mean = _background_sum_squared / _background_frame_count
    mean_squared = cv2.pow(_background_mean(), 2)
    return cv2.subtract(squared_sum_mean, mean_squared)

def _background_standard_dev():
    return cv2.pow(_background_variance(), 0.5)


def required_quality():
    return "low"

def process_data(data):
    global _background_frame_count, arguments
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
    
    if _background_sum is None:
        _update_background(np_frame)
        return

    motion_diff_abs = cv2.absdiff(np_frame, _background_mean())
    detected_motion_condition = motion_diff_abs > arguments['pixel_change_threshold_scale_factor'] * _background_standard_dev()
    detected_motion_pixels = np.extract(detected_motion_condition, motion_diff_abs)
    if len(detected_motion_pixels) < res[0]*res[1]*arguments['total_pixel_change_threshold'] or \
            _background_frame_count < arguments['background_frame_count_threshold']:
        _update_background(np_frame)

    return {"all": {"time": datetime.now(),
                    "timestamp": frame_info.timestamp,
                    "is_motion": len(detected_motion_pixels) > arguments['total_pixel_change_threshold'],
                    "motion_magnitude": len(detected_motion_pixels),
                    "frame_number": frame_info.index}}

def shutdown_module():
    LOGGER.debug("Shut down.")

def name():
    return "SimpleStatisticalMotion"