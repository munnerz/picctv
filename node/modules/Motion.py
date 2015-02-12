from datetime import datetime
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

_event_buffer = []
_last_timestamp = 0
_last_start_time = datetime.now()

testing = False

def _update_background(frame):
    global _background_model, _background_frame_count, _rapid_matching_candidates, _previous_frame, _stable_signal_candidates, _accurate_matching_candidates

    if _background_model is None:
        _background_model = frame
    elif _background_frame_count < settings.MOTION_BACKGROUND_FRAME_COUNT_THRESHOLD:
        # initial background modelling
        _background_model += (1 / _background_frame_count) * \
                                    np.subtract(frame, _background_model)
    else:
        #rapid matching
        _rapid_matching_candidates = np.equal(frame, _previous_frame)
        
        #stable signal trainer
        if _stable_signal_candidates is None:
            _stable_signal_candidates = _background_model # not sure if this is correct, perhaps frames[0]?
        t_stable_signal_candidates = frame

        logical_and_gt_mask = ~(np.logical_and(_rapid_matching_candidates, np.greater(frame, _stable_signal_candidates)))
        logical_and_lt_mask = ~(np.logical_and(_rapid_matching_candidates, np.less(frame, _stable_signal_candidates)))

        t = np.ma.array(t_stable_signal_candidates, mask=logical_and_gt_mask, copy=False)
        t += 1
        t = np.ma.array(t_stable_signal_candidates, mask=logical_and_lt_mask, copy=False)
        t -= 1

        _stable_signal_candidates = t_stable_signal_candidates

        #accurate matching
        _accurate_matching_candidates_mask = ~(np.equal(_stable_signal_candidates, frame))

#            print("Dims: bgmodel: %s, Frame: %s, rapid matching candidates: %s, stable signal %s, accurate matching %s" % (self._background_model.shape,
#                                                                                                                          frame.shape, 
#                                                                                                                          self._rapid_matching_candidates.shape, 
#                                                                                                                          self._stable_signal_candidates.shape, 
#                                                                                                                          self._accurate_matching_candidates_mask.shape))
        #background updating (8 is alpha in (20), and should be changed)

        subtracted = (1 / 8) * np.subtract(frame, _background_model) #change to only do this op on accurate matches
        
        t = np.ma.array(_background_model, mask=_accurate_matching_candidates_mask, copy=False)
        t += subtracted

    _background_frame_count += 1

def required_quality():
    return "low"

def process_frame(data):
    global process_frame, _first_diff_abs, _short_variance, _long_variance, _event_buffer, _last_start_time, _last_timestamp

    (frame, frame_info) = data

    res = settings._RECORDING_QUALITIES[required_quality()]['resolution']

    if(len(frame) < res[0] * res[1]):
        print ("Fake frame... (len: %d, expected: %d)" % (len(frame), res[0]*res[1]))
        return None # we have a fake frame!

    stream = open(settings.MOTION_TMP_FILE, 'w+b')
    stream.write(frame)
    stream.seek(0)

    np_frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).astype('float32').reshape((res[0], res[1]))
    
    _update_background(np_frame)

    motion_diff_abs = np.absolute(np.subtract(np_frame, _background_model))

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

    if testing:
        cv2.imshow("Image", _binary_motion_detection_mask.astype('float32'))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        return _binary_motion_detection_mask

    _motion_detected_pixels = len(np.extract(_binary_motion_detection_mask, _binary_motion_detection_mask))

    _event_buffer.append({"is_motion": _motion_detected_pixels > settings.MOTION_LEVEL,
                               "motion_magnitude": _motion_detected_pixels,
                               "frame_number": frame_info.index})

    _previous_frame = np_frame # save this frame as the previous one for next call

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
