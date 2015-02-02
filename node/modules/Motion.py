from datetime import datetime
import numpy as np
import cv2
import logging

from modules.ModuleBase import ModuleBase
import settings

LOGGER = logging.getLogger("node.Motion")

class Motion(ModuleBase):

    def __init__(self):
        ModuleBase.__init__(self)

        #initialise both of these to matrices of zeros
        self._background_sum = None
        self._background_sum_squared = None
        self._background_frame_count = 0 #the number of frames that comprise the background data

        self._last_timestamp = 0
        self._last_start_time = datetime.now()

    def _update_background(self, frame):
        if self._background_sum is None and self._background_sum_squared is None:
            self._background_sum = frame
            self._background_sum_squared = cv2.pow(frame, 2.0)
        else:
            cv2.accumulate(frame, self._background_sum)
            cv2.accumulateSquare(frame, self._background_sum_squared)
        self._background_frame_count += 1

    def _background_mean(self):
        return self._background_sum / self._background_frame_count

    def _background_variance(self):
        squared_sum_mean = self._background_sum_squared / self._background_frame_count
        mean_squared = cv2.pow(self._background_mean(), 2)
        return cv2.subtract(squared_sum_mean, mean_squared)

    def _background_standard_dev(self):
        return cv2.pow(self._background_variance(), 0.5)


    def required_quality(self):
        return "low"

    def process_frame(self, data):
        (frame, frame_info) = data

        res = settings._RECORDING_QUALITIES[self.required_quality()]['resolution']

        if(len(frame) < res[0] * res[1]):
            print ("Fake frame...")
            return None # we have a fake frame!

        stream = open(settings.MOTION_TMP_FILE, 'w+b')
        stream.write(frame)
        stream.seek(0)

        np_frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).astype('float32').reshape((res[1], res[0]))
        
        if(self._background_frame_count > settings.MOTION_BACKGROUND_FRAME_COUNT_THRESHOLD):
            motion_diff_abs = cv2.absdiff(np_frame, self._background_mean())
            detected_motion_condition = motion_diff_abs > settings.MOTION_PIXEL_CHANGE_THRESHOLD_SCALE_FACTOR * self._background_standard_dev()
            detected_motion_pixels = np.extract(detected_motion_condition, motion_diff_abs)
            if len(detected_motion_pixels) > res[0]*res[1]*settings.MOTION_TOTAL_PIXEL_CHANGE_THRESHOLD:
                print ("Detected motion. %d pixels have changed from our rolling average..." % len(detected_motion_pixels))

        #do this after analysis of current frame
        self._update_background(np_frame)

        return None

    def shutdown(self):
        LOGGER.debug("Shut down.")
