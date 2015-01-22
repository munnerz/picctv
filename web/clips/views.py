import os
import logging

from django.shortcuts import render
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.http import HttpResponse

import models
import tools

# --- view methods ---
def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def watch(request):
    if request.method == 'POST': # If the form has been submitted...
        form = models.ClipForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            clips = models.clip.objects.filter(camera_name=form.cleaned_data['camera_name']).filter(start_time__gte=form.cleaned_data['start_datetime'], end_time__lte=form.cleaned_data['end_datetime']).order_by('start_time')
            datetime_segments = tools.find_datetime_segments(clips)

            clips_fh = [c.data for c in clips]
            mp4_file = tools.wrap_h264(clips_fh)

            stream_url = "http://cctv.phlat493:81/%s" % os.path.basename(mp4_file.name)
            return render(request, 'clips/watch.html', {"clip_url": stream_url,
                                                        "datetime_segments": datetime_segments})
    
def list(request):

    camera_list = models.clip.objects.distinct("camera_name")

    return render(request, 'clips/list.html', {"cameras": camera_list,
                                               "search_form": models.ClipForm()
                                               })

def stream(request):
    return ""
