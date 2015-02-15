from datetime import datetime
from collections import Counter

import numpy as np
import cv2
import logging

import settings

LOGGER = logging.getLogger("node.Motion")

#initialise both of these to matrices of zeros
_previous_frame = None
_previous_background_model = None
_background_model = None
_background_frame_count = 0

_first_diff_abs = None
_rapid_matching_candidates = None
_stable_signal_candidates = None
_accurate_matching_candidates = None

_long_variance = None
_short_variance = None

_candidates = None

_event_buffer = []
_last_timestamp = 0
_last_start_time = datetime.now()


def P(a, w):
    o = np.zeros(a.shape, dtype='float32')
    o_ = o.reshape(-1)
    a = a.reshape(-1)
    for i, v in enumerate(a):
        o_[i] = np.extract(a, np.absolute(a - v) < 10).sum().astype('float32') / (w * w)
    return o

def A(p):
    T = 1
    e = p * np.log2(p)
    E = e.sum()
    if (-E) > T:
        return np.ones(p.shape, dtype=bool)
    else:
        return np.zeros(p.shape, dtype=bool)
	
def _update_background(frame):
    global _background_model, _background_frame_count, _previous_frame, _candidates

    if _background_model is None:
        _background_model = frame
    elif _background_frame_count < settings.MOTION_BACKGROUND_FRAME_COUNT_THRESHOLD:
        # initial background modelling
        _background_model += (1 / _background_frame_count) * \
                                    np.subtract(frame, _background_model)
    else:

        if _candidates is None:
            _candidates = frame

        #rapid matching
        _rapid_matching_candidates_mask = ~(np.absolute(frame - _previous_frame) < 10)

        _rapid_matching_candidates = np.ma.array(_candidates, mask=_rapid_matching_candidates_mask, copy=False)


        _candidates_gt = np.ma.array(_rapid_matching_candidates, mask=~(frame > _candidates), copy=False)
        _candidates_lt = np.ma.array(_rapid_matching_candidates, mask=~(frame < _candidates), copy=False)

        _candidates_gt += 1
        _candidates_lt -= 1

        _accurate_matching_candidates_mask = ~(_candidates == frame)

        _accurate_matches = np.ma.array(_background_model, mask=_accurate_matching_candidates_mask, copy=False)
        _accurate_matches += (frame - _accurate_matches)

        if settings.MOTION_TESTING:
            cv2.imshow("Rapid Matches", (~_rapid_matching_candidates_mask).astype('float32'))
            cv2.imshow("Accurate Matches", (~_accurate_matching_candidates_mask).astype('float32'))
            cv2.imshow("Background", _background_model)

    _background_frame_count += 1

def required_quality():
    return "low"

def process_frame(data):
    global process_frame, _first_diff_abs, _short_variance, _long_variance, _event_buffer, _last_start_time, _last_timestamp, _previous_frame

    (frame, frame_info) = data

    res = settings._RECORDING_QUALITIES[required_quality()]['resolution']

    if(len(frame) < res[0] * res[1]):
        print ("Fake frame... (len: %d, expected: %d)" % (len(frame), res[0]*res[1]))
        return None # we have a fake frame!

    stream = open(settings.MOTION_TMP_FILE, 'w+b')
    stream.write(frame)
    stream.seek(0)

    np_frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).reshape((res[1], res[0]))
    
    _update_background(np_frame)

    motion_diff_abs = np.absolute(np.subtract(np_frame, _background_model))


# not currently working...
#    p_values = np.zeros(shape=motion_diff_abs.shape)
#    a_values = np.zeros(shape=motion_diff_abs.shape, dtype=bool)
#    x = y = 0
#    w = 8
#    while x <= res[0] - w:
#        while y <= res[1] - w:
#            diff_block = motion_diff_abs[x:x+w, y:y+w]
#            p_values[x:x+w, y:y+w] = P(diff_block, w)
#            a_values[x:x+w, y:y+w] = A(p_values[x:x+w, y:y+w])
#            y += w
#        x += w

#    print ("A: %s" % a_values)
#    cv2.imshow("A-Values", a_values.astype('float32'))

    kernel = np.ones((4,4),np.uint8)
    motion_diff_abs = cv2.erode(motion_diff_abs,kernel,iterations = 2)
    motion_diff_abs = cv2.dilate(motion_diff_abs,kernel,iterations = 1)

    if _first_diff_abs is None:
        _first_diff_abs = motion_diff_abs # this should possibly be the second abs diff,
                                               # as this first will be all zeroes

    # now, as per B. alarms trigger module, we should split the image into w x w blocks,
    # take the average grey of them, and work with that

    if _short_variance is None:
        _short_variance = _first_diff_abs

    N = 2

    _short_variance_gt_mask = ~(np.greater(N * motion_diff_abs, _short_variance))
    _short_variance_lt_mask = ~(np.less(N * motion_diff_abs, _short_variance))

    t = np.ma.array(_short_variance, mask=_short_variance_gt_mask, copy=False)
    t += 1

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
    t += 1

    t = np.ma.array(_long_variance, mask=_long_variance_lt_mask, copy=False)
    t -= 1

    _best_variance = N * np.minimum(_long_variance, _short_variance)

    _binary_motion_detection_mask = motion_diff_abs > _best_variance

    if settings.MOTION_TESTING:
        cv2.imshow("Frame", np_frame)
        cv2.imshow("Difference", _binary_motion_detection_mask.astype('float32'))

    _motion_detected_pixels = len(np.extract(_binary_motion_detection_mask, _binary_motion_detection_mask))

    _event_buffer.append({"is_motion": _motion_detected_pixels > settings.MOTION_LEVEL,
                               "motion_magnitude": _motion_detected_pixels,
                               "frame_number": frame_info.index})

    _previous_frame = np_frame # save this frame as the previous one for next call

    cv2.waitKey(1)

    # actually send data off (or don't, depending on amount of data)
    if len(_event_buffer) > settings.MOTION_CHUNK_LENGTH:
        data_buffer = _event_buffer[:]
        _event_buffer = []

        end_time = datetime.now()
        end_timestamp = frame_info.timestamp

        to_send = dict(start_time=_last_start_time,
                       end_time=end_time,
                       start_timestamp=_last_timestamp,
                       end_timestamp=end_timestamp,
                       data_buffer=data_buffer)

        _last_start_time = end_time
        _last_timestamp = end_timestamp

        return to_send
    else:
        return None

def shutdown():
    LOGGER.debug("Shut down.")
