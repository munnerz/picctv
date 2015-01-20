import logging
from datetime import datetime

from picamera import PiVideoFrameType

from modules.ModuleBase import ModuleBase

LOGGER = logging.getLogger("node.Recording")

class Recording(ModuleBase):

    def __init__(self):
        self.buffer = b''
        self._last_timestamp = 0
        self._last_frame_index = 0
        self._last_start_time = datetime.now()

    def required_quality(self):
        return "high"

    def process_frame(self, data):
        (frame, info) = data

        if len(self.buffer) > 1024 * 1024 and info.frame_type == PiVideoFrameType.sps_header:
            data_to_send = self.buffer[:]
            self.buffer = frame

            end_time = datetime.now()
            to_send = {"frame_data": data_to_send, 
                       "start_frame_index": self._last_frame_index,
                       "end_frame_index": info.index,
                       "start_timestamp": self._last_timestamp,
                       "end_timestamp": info.timestamp,
                       "start_time": self._last_start_time,
                       "end_time": end_time}

            self._last_timestamp = info.timestamp
            self._last_frame_index = info.index
            self._last_start_time = end_time

            return to_send
        else:
            self.buffer = b''.join([self.buffer, frame])
            return None


    def shutdown(self):
        ModuleBase.shutdown(self)
        LOGGER.info("Shutting down %s" % self.get_name())
        return