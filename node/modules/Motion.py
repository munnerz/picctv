from datetime import datetime
import numpy as np
import cv2
import logging

import settings

LOGGER = logging.getLogger("node.Motion")

_frames = []
_frameLimit = 5
_MOTION_LEVEL = settings.MOTION_LEVEL
_THRESHOLD = settings.MOTION_THRESHOLD
_event_buffer = []
_last_timestamp = 0
_last_start_time = datetime.now()

def _storeFrame(frame):
    _frames.insert(0, frame)
    if len(_frames) > _frameLimit:
        _frames.pop(len(_frames) - 1)

def _getMotion():
    d1 = cv2.absdiff(_frames[1], _frames[0])
    d2 = cv2.absdiff(_frames[2], _frames[0])
    result = cv2.bitwise_and(d1, d2)

    (value, r) = cv2.threshold(result, _THRESHOLD, 255, cv2.THRESH_BINARY)

    scalar = cv2.sumElems(r)

    return scalar

def process_frame(frame):
    _storeFrame(frame)
    m = 0
    if len(_frames) >= 3:
        motion = _getMotion()
        m = motion[0]
        if motion and motion[0] > _MOTION_LEVEL:
            LOGGER.debug("Detected motion! Level: %d" % motion[0])
            return (True, m)

    return (False, m)

def required_quality():
    return "low"

def shutdown():
    LOGGER.debug("Shut down.")
