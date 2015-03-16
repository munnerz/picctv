import logging
from subprocess import Popen, PIPE, STDOUT
from tempfile import _get_candidate_names
from datetime import timedelta
from models import analysis, clip

def wrap_h264(clips):
    _out_file = open('/run/shm/tmp/%s' % _get_candidate_names().next(), 'w+b')
    
    try:
        p = Popen(["/usr/local/bin/ffmpeg",
                    "-y", "-an", "-i", "-",
                    "-vcodec", "copy",
                    "-movflags", "faststart",
                    "-f", "mp4", _out_file.name],
                    stdin=PIPE)
        for clip in clips:
            while True:
                d = clip.read(8192)
                if d:
                    p.stdin.write(d)
                else:
                    break
        p.stdin.close()
        p.wait()
        return _out_file
    except Exception as e:
        from traceback import print_exc
        print_exc(e)
        logging.getLogger("views").info("ERROR: %s" % e)

    return None

def find_datetime_segments(clips):
    last_segment_start = last_clip_end = False
    segments = []
    for clip in clips:
        if clip.start_time != last_clip_end:
            if last_segment_start and last_clip_end:
                segments.append((last_segment_start, last_clip_end))
            last_segment_start = clip.start_time
        last_clip_end = clip.end_time
    if last_clip_end and last_segment_start:
        segments.append((last_segment_start, last_clip_end))
    return segments

def get_analysis_chunks(datetime_segment, camera, module=None):
    (start, end) = datetime_segment
    return [x.data for x in analysis.objects.filter(module_name=module, camera_name=camera).filter(data__start_time__gte=start, data__end_time__lte=end)]

def chain_events(chunks, start_field, end_field, trigger_data, is_triggered, shortcut=lambda _: None):
    create_event = lambda x, y: {"camera_name": x.camera_name,
                                 "module_name": x.module_name,
                                 "start_time":  start_field(x),
                                 "end_time":    end_field(y),
                                 "length":      end_field(y) - start_field(x)}
    events = []
    event_end = {}
    event_start = {}
    for chunk in chunks:
        try:
            chunk_triggered = shortcut(chunk)
            if chunk_triggered is None:
                true_events = sum(map(is_triggered, trigger_data(chunk)))
                chunk_triggered = true_events / len(trigger_data(chunk)) > 0.2

            if chunk_triggered:
                if event_end.get(chunk.module_name) is None:
                    event_start[chunk.module_name] = chunk
                    event_end[chunk.module_name] = chunk
                elif start_field(event_start[chunk.module_name]) == end_field(chunk):
                    event_start[chunk.module_name] = chunk
                else:
                    events.append(create_event(event_start[chunk.module_name], event_end[chunk.module_name]))
                    event_start[chunk.module_name] = chunk
                    event_end[chunk.module_name] = chunk
            else:
                if event_end.get(chunk.module_name) is not None:
                    events.append(create_event(event_start[chunk.module_name], event_end[chunk.module_name]))
                event_start[chunk.module_name] = None
                event_end[chunk.module_name] = None
        except TypeError as e:
            print ("type error: %s" % e)
            pass

    for key,value in event_end.items():
        if event_start.get(key) is not None:
            events.append(create_event(event_start[key], event_end[key]))

    return events


# when adding a module with a weird data type, you'll need to write a custom handler here
# look at chain_events and how it is used in order to write the correct lambda functions
def get_recent_events(camera_name, include_recordings=True):
    print ("Getting events for %s" % camera_name)
    analysis_chunks = analysis.objects.filter(camera_name=camera_name).order_by('-data.end_time').limit(200)

    events = chain_events(analysis_chunks, 
                          lambda x: x.data[0]['time'] if type(x.data) is list else x.data['start_time'],
                          lambda x: x.data[-1]['time'] if type(x.data) is list else x.data['end_time'],
                          lambda x: x.data.get('data_buffer') if type(x.data.get('data_buffer', None)) is list else x.data,
                          lambda x: 1 if x['is_motion'] else 0,
                          lambda x: getattr(x, 'triggered', None)
                          )

    if include_recordings:
        recording_chunks = clip.objects.filter(camera_name=camera_name).order_by('-end_time').limit(200)
        events += chain_events(recording_chunks,
                               lambda x: x['start_time'],
                               lambda x: x['end_time'],
                               lambda _: [1],
                               lambda _: True
                               )


    return events
            