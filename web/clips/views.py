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
        start_datetime = float(request.GET['start_datetime'])
        end_datetime = float(request.GET['end_datetime'])
        if start_datetime < 0:
            start_datetime = end_datetime + start_datetime
        form = models.ClipForm({"start_datetime":   datetime.fromtimestamp(start_datetime),
                                "end_datetime":     datetime.fromtimestamp(end_datetime),
                                "camera_name":      request.GET['camera_name']})

    if form.is_valid(): # All validation rules pass
        from itertools import chain
        # retrieve all clips between the entered datetimes
        # allow 15 seconds either side to ensure the datetimes
        # requested are included in the video
        clips = models.clip.objects.filter(camera_name=form.cleaned_data['camera_name']).filter(start_time__gte=form.cleaned_data['start_datetime']-timedelta(seconds=15), end_time__lte=form.cleaned_data['end_datetime']+timedelta(seconds=15)).order_by('start_time')

        datetime_segments = tools.find_datetime_segments(clips)
        if len(datetime_segments) > 0:
            mp4_file = tools.wrap_h264([c.data for c in clips])
            start_datetime = None
            c = None
            for c in clips:
                if start_datetime is None:
                    start_datetime = c.start_time
            end_datetime = c.end_time
            if mp4_file:
                camera_list = models.clip.objects.distinct("camera_name")
                return render(request, 'clips/watch.html', {"clip_url": "http://cctv.phlat493/stream/%s" % os.path.basename(mp4_file.name),
                                                            "camera_name": form.cleaned_data['camera_name'],
                                                            "cameras": camera_list,
                                                            "search_form": models.ClipForm(),
                                                            "start_datetime": start_datetime,
                                                            "end_datetime": end_datetime,
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

def camera(request, camera_name):
    camera_list = models.clip.objects.distinct("camera_name")
    unsorted_events = tools.get_recent_events(camera_name)
    events_list = sorted(unsorted_events, key=lambda x: x['end_time'], reverse=True)
    now = datetime.now()
    start_datetime = now-timedelta(seconds=45)
    end_datetime = now
    clips = models.clip.objects.filter(camera_name=camera_name).filter(start_time__gte=start_datetime, end_time__lte=end_datetime).order_by('start_time')
    mp4_file = tools.wrap_h264([c.data for c in clips])
    _start_datetime = None
    c = None
    for c in clips:
        if _start_datetime is None:
            _start_datetime = c.start_time
    start_datetime = _start_datetime
    end_datetime = c.end_time
    return render(request, 'clips/camera.html', {"cameras": camera_list,
                                                 "clip_url": "http://cctv.phlat493/stream/%s" % os.path.basename(mp4_file.name),
                                                 "search_form": models.ClipForm(),
                                                 "recent_motion_chart": tools.generate_motion_graph(camera_name, [(now-timedelta(minutes=15),now)]),
                                                 "events_list": events_list,
                                                 "camera_name": camera_name,
                                                 "start_datetime": start_datetime,
                                                 "end_datetime": end_datetime, })

