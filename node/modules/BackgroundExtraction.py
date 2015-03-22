import numpy as np
import cv2

from node import settings

LOGGER = settings.logger("node.modules.BackgroundExtraction")

arguments = None
_background_model = None
_background_frame_count = 0
_candidates = None
_previous_frame = None

def process_data(data):
    global _background_model, _background_frame_count, _previous_frame, _candidates, arguments

    (module, data) = data
    (frame, frame_info) = data

    res = arguments['resolution']

    stream = open(arguments['tmp_file'], 'w+b')
    stream.write(frame)
    stream.seek(0)

    frame = np.fromfile(stream, dtype='uint8', count=res[1]*res[0]).reshape((res[1], res[0])).astype(np.float32)
    frame = frame / 255

    if _background_model is None:
        _background_model = frame
    elif _background_frame_count < arguments['frame_count_threshold']:
        # initial background modelling
        _background_model += (1 / _background_frame_count) * \
                                    np.subtract(frame, _background_model)
    else:

        if _candidates is None:
            _candidates = frame

        #rapid matching
        _rapid_matching_candidates_mask = ~(np.absolute(frame - _previous_frame) < (1.0/255.0)) # the threshold for a change in pixel value to register as rapid matching

        _rapid_matching_candidates = np.ma.array(_candidates, mask=_rapid_matching_candidates_mask, copy=False)

        _candidates_gt = np.ma.array(_rapid_matching_candidates, mask=~(frame > _candidates), copy=False)
        _candidates_lt = np.ma.array(_rapid_matching_candidates, mask=~(frame < _candidates), copy=False)

        _candidates_gt += 0.5 / 255.0 # make this smaller to make the algorithm accept a change in pixel colour quicker
        _candidates_lt -= 0.5 / 255.0 # eg. the smaller this number, the quicker the background will accept the new colour as truth

        _accurate_matching_candidates_mask = ~(_candidates - frame < (0.2/255.0)) # increase this fraction to 'accept' new background pixels quicker

        _accurate_matches = np.ma.array(_background_model, mask=_accurate_matching_candidates_mask, copy=False)
        _accurate_matches += (frame - _accurate_matches) * (0.0625)  # this should be a small increment, else we'll keep shooting either side of the actual value
                                                                 # the greater the factor, the quicker the background will actually take on new colours (once it has accepted the
                                                                 # colour has changed by _candidates == frame

    _background_frame_count += 1

    _previous_frame = frame
    return {"all": (_background_model*255).astype(np.uint8)}

def name():
    return "BackgroundExtraction"
