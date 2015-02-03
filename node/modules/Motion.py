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
        self._previous_frame = None
        self._previous_background_model = None
        self._background_model = None
        self._background_frame_count = 0

        self._first_diff_abs = None
        self._rapid_matching_candidates = None
        self._stable_signal_candidates = None
        self._accurate_matching_candidates = None

        self._long_variance = None
        self._short_variance = None

        self._last_timestamp = 0
        self._last_start_time = datetime.now()

    def _update_background(self, frame):
        if self._background_model is None:
            self._background_model = frame
        elif self._background_frame_count < settings.MOTION_BACKGROUND_FRAME_COUNT_THRESHOLD:
            # initial background modelling
            self._background_model += (1 / self._background_frame_count) * \
                                        np.subtract(frame, self._background_model)
        else:
            #rapid matching
            self._rapid_matching_candidates = np.equal(frame, self._previous_frame)
            
            #stable signal trainer
            if self._stable_signal_candidates is None:
                self._stable_signal_candidates = self._background_model # not sure if this is correct, perhaps frames[0]?
            t_stable_signal_candidates = frame

            logical_and_gt_mask = ~(np.logical_and(self._rapid_matching_candidates, np.greater(frame, self._stable_signal_candidates)))
            logical_and_lt_mask = ~(np.logical_and(self._rapid_matching_candidates, np.less(frame, self._stable_signal_candidates)))

            t = np.ma.array(t_stable_signal_candidates, mask=logical_and_gt_mask, copy=False)
            t += 1
            t = np.ma.array(t_stable_signal_candidates, mask=logical_and_lt_mask, copy=False)
            t -= 1

            self._stable_signal_candidates = t_stable_signal_candidates

            #accurate matching
            self._accurate_matching_candidates_mask = ~(np.equal(self._stable_signal_candidates, frame))

#            print("Dims: bgmodel: %s, Frame: %s, rapid matching candidates: %s, stable signal %s, accurate matching %s" % (self._background_model.shape,
#                                                                                                                          frame.shape, 
#                                                                                                                          self._rapid_matching_candidates.shape, 
#                                                                                                                          self._stable_signal_candidates.shape, 
#                                                                                                                          self._accurate_matching_candidates_mask.shape))
            #background updating (8 is alpha in (20), and should be changed)

            subtracted = (1 / 8) * np.subtract(frame, self._background_model) #change to only do this op on accurate matches
            
            t = np.ma.array(self._background_model, mask=self._accurate_matching_candidates_mask, copy=False)
            t += subtracted

        self._background_frame_count += 1

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
        
        self._update_background(np_frame)

        motion_diff_abs = np.absolute(np.subtract(np_frame, self._background_model))

        if self._first_diff_abs is None:
            self._first_diff_abs = motion_diff_abs # this should possibly be the second abs diff,
                                                   # as this first will be all zeroes

        # now, as per B. alarms trigger module, we should split the image into w x w blocks,
        # take the average grey of them, and work with that

        if self._short_variance is None:
            self._short_variance = self._first_diff_abs

        N = 2


        _short_variance_gt_mask = ~(np.greater(N * motion_diff_abs, self._short_variance))
        _short_variance_lt_mask = ~(np.less(N * motion_diff_abs, self._short_variance))

        t = np.ma.array(self._short_variance, mask=_short_variance_gt_mask, copy=False)
        t += 1

        t = np.ma.array(self._short_variance, mask=_short_variance_lt_mask, copy=False)
        t -= 1


        if self._long_variance is None:
            self._long_variance = self._first_diff_abs

        # these are sort of swapped, as an efficiency improvement.
        # masks are represented inverted (ie. True values ARE masked), we need
        # to invert the result to make values we WANT, be False. This is it:
        _long_variance_gt_mask = np.less(self._short_variance, self._long_variance)
        _long_variance_lt_mask = np.greater(self._short_variance, self._long_variance)

        t = np.ma.array(self._long_variance, mask=_long_variance_gt_mask, copy=False)
        t += 1

        t = np.ma.array(self._long_variance, mask=_long_variance_lt_mask, copy=False)
        t -= 1

        _best_variance = N * np.minimum(self._long_variance, self._short_variance)

        _binary_motion_detection_mask = motion_diff_abs > _best_variance

        print("%d pixels changed" % len(np.extract(_binary_motion_detection_mask, _binary_motion_detection_mask)))

        self._previous_frame = np_frame # save this frame as the previous one for next call
        return None

    def shutdown(self):
        LOGGER.debug("Shut down.")
