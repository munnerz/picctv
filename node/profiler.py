import sys
import logging

import cv2
import numpy as np

from modules import Motion

log = None

class FrameInfo(object):
    ''' this provides the minimum implementation of frame_info so that
        motion detection can be tested '''

    def __init__(self, index, timestamp):
        self.index = index
        self.timestamp = timestamp

def setup_logger():
    global log
    log = logging.getLogger(name="profiler")
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    log.addHandler(ch)

if __name__ == "__main__":
    setup_logger()
    cv2.namedWindow("Image")
    if len(sys.argv) < 2:
        log.error("Usage profiler.py <video_clip_path>")
        sys.exit(1)

    Motion.testing = True

    vid_clip_path = sys.argv[1]
    vid_cap = cv2.VideoCapture(vid_clip_path)

    frame_count = 0
    # get initial frame
    success, frame = vid_cap.read()
    while success:
        # we set timestamp to frame_count for now as it doesn't
        # really matter..
        frame_info = FrameInfo(frame_count, frame_count)
        frame_count += 1

        frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).flatten()

        moved_pixels = Motion.process_frame((frame_yuv, frame_info)).astype('float32')

        cv2.imshow("Image", moved_pixels)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        log.info("There have been %d moved pixels" % (len(np.extract(moved_pixels, moved_pixels))) )
        # get next frame
        success, frame = vid_cap.read()
        