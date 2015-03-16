_background_model = None
_background_frame_count = 0
_candidates = None
_previous_frame = None

def process_data(data):
    global _background_model, _background_frame_count, _previous_frame, _candidates
    
    (module, data) = data
    (frame, frame_info) = data

    if _background_model is None:
        _background_model = frame
    elif _background_frame_count < arguments['background_frame_count_threshold']:
        # initial background modelling
        _background_model += (1 / _background_frame_count) * \
                                    np.subtract(frame, _background_model)
    else:

        if _candidates is None:
            _candidates = frame

        #rapid matching
        _rapid_matching_candidates_mask = ~(np.absolute(frame - _previous_frame) < 10)

        _rapid_matching_candidates = np.ma.array(_candidates, mask=_rapid_matching_candidates_mask, copy=False)


        _candidates_gt = np.ma.array(_rapid_matching_candidates, mask=~(frame > _candidates), copy=False)
        _candidates_lt = np.ma.array(_rapid_matching_candidates, mask=~(frame < _candidates), copy=False)

        _candidates_gt += 1
        _candidates_lt -= 1

        _accurate_matching_candidates_mask = ~(_candidates == frame)

        _accurate_matches = np.ma.array(_background_model, mask=_accurate_matching_candidates_mask, copy=False)
        _accurate_matches += (frame - _accurate_matches)

    _background_frame_count += 1

    _previous_frame = np_frame

    return {"all": _background_model}

def name():
    return "BackgroundExtraction"