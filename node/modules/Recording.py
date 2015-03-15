import logging
from datetime import datetime

from picamera import PiVideoFrameType

import settings

LOGGER = settings.logger("node.modules.Recording")

sbuffer = []
_last_timestamp = 0
_last_frame_index = 0
_last_start_time = datetime.now()

def required_quality():
    return "high"

def process_data(data):
    global sbuffer, _last_timestamp, _last_frame_index, _last_start_time
    (_, data) = data
    (frame, info) = data

    if info.frame_type == PiVideoFrameType.sps_header and (datetime.now() - _last_start_time).seconds > arguments['chunk_length']:
        data_to_send = b''.join(sbuffer)
        sbuffer = [frame]

        end_time = datetime.now()
        to_send = {"frame_data": data_to_send, 
                   "start_frame_index": _last_frame_index,
                   "end_frame_index": info.index,
                   "start_timestamp": _last_timestamp,
                   "end_timestamp": info.timestamp,
                   "start_time": _last_start_time,
                   "end_time": end_time}

        _last_timestamp = info.timestamp
        _last_frame_index = info.index
        _last_start_time = end_time

        return to_send
    else:
        sbuffer.append(frame)
        return None

def name():
  return "Recording"
  
def shutdown():
    LOGGER.debug("Shut down.")