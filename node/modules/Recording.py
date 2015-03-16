# Description: This module accepts (frame, frame_info) tuples, it
#              creates a running buffer of the frames and implements
#              its own custom buffering so as to include custom metadata.
#
# Inputs:      (frame, frame_info)
# Output:      {"frame_data": _, #all the frame data in this chunk
#               "start_frame_index": _, # the index of the first frame in this chunk
#               "end_frame_index": _, # the index of the last frame in this chunk
#               "start_timestamp": _, # the first timestamp in this chunk
#               "end_timestamp": _, # the last timestamp in the chunk
#               "start_time": _,  # datetime object containing the start time of this chunk
#               "end_time": _} # datetime object containing the end time of this chunk

import logging
from datetime import datetime

from picamera import PiVideoFrameType

import settings

LOGGER = settings.logger("node.modules.Recording")

sbuffer = []
_last_timestamp = 0
_last_frame_index = 0
_last_start_time = datetime.now()

def process_data(data):
    global sbuffer, _last_timestamp, _last_frame_index, _last_start_time
    (_, data) = data
    (frame, info) = data

    if info.frame_type == PiVideoFrameType.sps_header and (datetime.now() - _last_start_time).seconds > arguments['chunk_length']:
        data_to_send = b''.join(sbuffer)
        sbuffer = [frame]

        end_time = datetime.now()
        to_send = {"all": {"frame_data": data_to_send, 
                           "start_frame_index": _last_frame_index,
                           "end_frame_index": info.index,
                           "start_timestamp": _last_timestamp,
                           "end_timestamp": info.timestamp,
                           "start_time": _last_start_time,
                           "end_time": end_time
                          }
                        }

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