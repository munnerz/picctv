from subprocess import Popen
import os
import sys
from tempfile import _get_candidate_names, NamedTemporaryFile
from datetime import datetime
import logging

from django.shortcuts import render
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.http import HttpResponse

import models

# --- helper methods ---
def wrap_h264(_in_file):
    _out_file = open('/run/shm/tmp/%s' % _get_candidate_names().next(), 'w+b')

    _in_file.seek(0)

    logging.getLogger("views").info("_in_file: %s, _out_file: %s" % (_in_file.name, _out_file.name))
    
    try:
        p = Popen(["/usr/local/bin/ffmpeg",
                    "-y", "-an", "-i", "-",
                    "-vcodec", "copy",
                    "-movflags", "faststart",
                    "-f", "mp4", _out_file.name],
                    stdin=_in_file)
        p.wait()
        return _out_file
    except Exception as e:
        from traceback import print_exc
        print_exc(e)
        logging.getLogger("views").info("ERRROR: %s" % e)

    return None

# --- view methods ---
def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def watch(request):
    logging.getLogger("views").info("Watch received...")
    if request.method == 'POST': # If the form has been submitted...
        logging.getLogger("views").info("POST")
        form = models.ClipForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            logging.getLogger("views").info("Valid")
            clips = models.clip.objects.filter(camera_name=form.cleaned_data['camera_name']).filter(start_time__gte=form.cleaned_data['start_datetime'], end_time__lte=form.cleaned_data['end_datetime']).order_by('start_time')
            logging.getLogger("views").info("Got")
            _in_file = NamedTemporaryFile(dir='/run/shm/tmp/')
            for c in clips:
                logging.getLogger("views").info("Read/writing next file...")
                while True:
                    data = c.data.read(4096)
                    if not data:
                        break
                    _in_file.write(data)

            _in_file.flush()
            mp4_file = wrap_h264(_in_file)
            _in_file.close()

            stream_url = "http://cctv.phlat493:81/%s" % os.path.basename(mp4_file.name)
            return render(request, 'clips/watch.html', {"clip_url": stream_url})
    
def list(request, camera_name=''):
    page = int(request.GET.get('p', 1))
    limit = int(request.GET.get('l', 15))
    offset = int((page - 1) * limit)

    camera_list = models.clip.objects.distinct("camera_name")
    all_clips = models.clip.objects.order_by('-end_time')
    if(camera_name == ''):
        current_camera_clips = all_clips
    else:
        current_camera_clips = models.clip.objects.filter(camera_name=camera_name)

    camera_list_ = dict()
    for camera in camera_list:
        camera_list_[camera] = all_clips.filter(camera_name=camera).count()
    camera_list = camera_list_

    paginator = Paginator(current_camera_clips.order_by("-end_time"), limit)
    
    start_page = page - 8
    if(start_page < 1):
        start_page = 1
    end_page = start_page + 18
    if(end_page > paginator.num_pages):
        end_page = paginator.num_pages + 1
    page_nav_range = xrange(start_page, end_page, 1)

    return render(request, 'clips/list.html', {"cameras": camera_list,
                                               "all_clips": all_clips,
                                               "camera_name": camera_name,
                                               "page_num": page,
                                               "paginator": paginator,
                                               "camera_clips": paginator.page(page),
                                               "page_nav_range": page_nav_range,
                                               "search_form": models.ClipForm()
                                               })

def detail(request, clip_id):
    return render(request, 'clips/detail.html', {'clip_id': clip_id})

def analysis(request):
    return render(request, 'clips/analysis.html', {"data": models.analysis.objects[:30]})
