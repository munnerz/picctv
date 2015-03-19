import os
import logging

from datetime import datetime, timedelta

from django.shortcuts import render
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.http import HttpResponse

from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

import models
import tools

# --- view methods ---
def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def watch(request):
    error = "An unrecognised error occured whilst loading the video!"
    if request.method == 'POST':
        form = models.ClipForm(request.POST)
    else:
        print(datetime.fromtimestamp(float(request.GET['start_datetime'])))
        form = models.ClipForm({"start_datetime":   datetime.fromtimestamp(float(request.GET['start_datetime'])),
                                "end_datetime":     datetime.fromtimestamp(float(request.GET['end_datetime'])),
                                "camera_name":      request.GET['camera_name']})

    if form.is_valid(): # All validation rules pass
        from itertools import chain
        clips = models.clip.objects.filter(camera_name=form.cleaned_data['camera_name']).filter(start_time__gte=form.cleaned_data['start_datetime']-timedelta(seconds=15), end_time__lte=form.cleaned_data['end_datetime']+timedelta(seconds=15)).order_by('start_time')

        datetime_segments = tools.find_datetime_segments(clips)
        if len(datetime_segments) > 0:
            motion_chunks = []

            clips_fh = [c.data for c in clips]

            mp4_file = tools.wrap_h264(clips_fh)

            if mp4_file:

                return render(request, 'clips/watch.html', {"clip_url": "http://cctv.phlat493/stream/%s" % os.path.basename(mp4_file.name),
                                                            "datetime_segments": datetime_segments,
                                                            "motion_data": tools.generate_motion_graph(form.cleaned_data['camera_name'], datetime_segments)})
            else:
                error = "Error creating MP4 file from chunks..."
        else:
            error = "No clips found..."
    else:
        error = "Invalid form entry..."

    return render(request, "clips/error.html", {"error": error})
    
def list(request):
    camera_list = models.clip.objects.distinct("camera_name")
    unsorted_events = map(tools.get_recent_events, camera_list)
    events_list = sorted([j for i in unsorted_events for j in i], key=lambda x: x['end_time'], reverse=True)

    return render(request, 'clips/list.html', {"cameras": camera_list,
                                               "search_form": models.ClipForm(),
                                               "events_list": events_list,
                                               })

def camera(request):
    return
