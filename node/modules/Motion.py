from datetime import datetime
import numpy as np
import cv2
import logging

from node.modules.ModuleBase import ModuleBase
from node import settings

LOGGER = logging.getLogger("node.Motion")

class Motion(ModuleBase):

    def __init__(self):
        ModuleBase.__init__(self)
        self._frames = []
        self._frameLimit = 5
        self._MOTION_LEVEL = settings.MOTION_LEVEL
        self._THRESHOLD = settings.MOTION_THRESHOLD
        self._event_buffer = []

        self._last_timestamp = 0
        self._last_start_time = datetime.now()

    def _storeFrame(self, frame):
        self._frames.insert(0, frame)
        if len(self._frames) > self._frameLimit:
            self._frames.pop(len(self._frames) - 1)

    def _getMotion(self):
        d1 = cv2.absdiff(self._frames[1], self._frames[0])
        d2 = cv2.absdiff(self._frames[2], self._frames[0])
        result = cv2.bitwise_and(d1, d2)

        (value, r) = cv2.threshold(result, self._THRESHOLD, 255, cv2.THRESH_BINARY)

        scalar = cv2.sumElems(r)

        return scalar

    def _analyse(self, frame):
        self._storeFrame(frame)
        m = 0
        if len(self._frames) >= 3:
            motion = self._getMotion()
            m = motion[0]
            if motion and motion[0] > self._MOTION_LEVEL:
                LOGGER.debug("Detected motion! Level: %d" % motion[0])
                return (True, m)

        return (False, m)


    def required_quality(self):
        return "low"

    def process_frame(self, data):
        (frame, frame_info) = data
        
        stream = open(settings.MOTION_TMP_FILE, 'w+b')
        stream.write(frame)
        stream.seek(0)

        res = settings._RECORDING_QUALITIES[self.required_quality()]['resolution']

        (is_motion, motion_val) = self._analyse(
                                        np.fromfile(stream, dtype=np.uint8, count=res[0] * res[1])
                                    .reshape(res))

        if len(self._event_buffer) > settings.MOTION_CHUNK_LENGTH:
            data_buffer = self._event_buffer[:]
            self._event_buffer = []

            end_time = datetime.now()
            end_timestamp = frame_info.timestamp

            to_send = dict(start_time=self._last_start_time,
                           end_time=end_time,
                           start_timestamp=self._last_timestamp,
                           end_timestamp=end_timestamp,
                           data_buffer=data_buffer)

            self._last_start_time = end_time
            self._last_timestamp = end_timestamp

            return to_send
        else:
            self._event_buffer.append({"is_motion": is_motion,
                                       "motion_magnitude": motion_val,
                                       "frame_number": frame_info.index})
            return None

    def shutdown(self):
        LOGGER.debug("Shut down.")
