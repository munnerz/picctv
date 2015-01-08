from modules.ModuleBase import ModuleBase
import numpy as np
import cv2

class Motion(ModuleBase):

    def __init__(self):
        ModuleBase.__init__(self)
        self._frames = []
        self._frameLimit = 5
        self._MOTION_LEVEL = 10000
        self._THRESHOLD = 35
        self._event_buffer = []

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
                print ("Detected motion level: %d" % motion[0])
                return (True, m)

        return (False, m)


    def required_quality(self):
        return "low"

    def process_frame(self, data):
        (frame, frameInfo) = data
        
        stream=open('/run/shm/picamtemp.dat','w+b')
        stream.write(frame)
        stream.seek(0)

        (is_motion, motion_val) = self._analyse(np.fromfile(stream, dtype=np.uint8, count=128*64).reshape((64, 128)))

        if len(self._event_buffer) > 100:
            to_send = self._event_buffer[:]
            self._event_buffer = []
            return to_send
        else:
            self._event_buffer.append((is_motion, motion_val))
            return None

    def shutdown(self):
        ModuleBase.shutdown(self)
        print ("Shutting down %s" % self.get_name())
        return