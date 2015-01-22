import logging
from subprocess import Popen, PIPE, STDOUT
from tempfile import _get_candidate_names

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
        logging.getLogger("views").info("ERRROR: %s" % e)

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
    segments.append((last_segment_start, last_clip_end))
    return segments

#def get_analysis_chunks(datetime_segment, module=None):
