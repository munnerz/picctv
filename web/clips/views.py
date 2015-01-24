import os
import logging

from bson import ObjectId
from django.shortcuts import render
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.http import HttpResponse
from django_downloadview import PathDownloadView
from graphos.sources.simple import SimpleDataSource
from graphos.renderers import flot

import models
import tools

# --- view methods ---
def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def watch(request):
    error = "An unrecognised error occured whilst loading the video!"
    if request.method == 'POST': # If the form has been submitted...
        form = models.ClipForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            clips = models.clip.objects.filter(camera_name=form.cleaned_data['camera_name']).filter(start_time__gte=form.cleaned_data['start_datetime'], end_time__lte=form.cleaned_data['end_datetime']).order_by('start_time')
            if len(clips) > 0:
                datetime_segments = tools.find_datetime_segments(clips)
                motion_chunks = []

                clips_fh = [c.data for c in clips]
                mp4_file = tools.wrap_h264(clips_fh)

                if mp4_file:

                    graph_data = [
                        ['Frame No.', 'Motion']
                    ]

                    for seg in datetime_segments:
                        chunk = tools.get_analysis_chunks(seg, form.cleaned_data['camera_name'], "Motion")
                        for x in chunk:
                            [graph_data.append([c['frame_number'], c['motion_magnitude']]) for c in x['data_buffer']]
                    
                    chart = flot.LineChart(SimpleDataSource(data=graph_data), width='100%')

                    db_mp4 = models.EncodedMP4()
                    db_mp4.path = "/run/shm/tmp/%s" % os.path.basename(mp4_file.name)
                    db_mp4.save()

                    return render(request, 'clips/watch.html', {"clip_id": str(db_mp4.id),
                                                                "datetime_segments": datetime_segments,
                                                                "motion_data": chart})
                else:
                    error = "Error creating MP4 file from chunks..."
            else:
                error = "No clips found..."
        else:
            error = "Invalid form entry..."
    else:
        error = "Invalid form entry..."
    return render(request, "clips/error.html", {"error": error})
    
def list(request):

    camera_list = models.clip.objects.distinct("camera_name")

    return render(request, 'clips/list.html', {"cameras": camera_list,
                                               "search_form": models.ClipForm()
                                               })

class DynamicStorageDownloadView(PathDownloadView):
    """Serve file of storage by path.upper()."""
    def get_path(self):
        """Return uppercase path."""
        the_id = super(DynamicStorageDownloadView, self).get_path()
        path = models.EncodedMP4.objects.filter(id=ObjectId(the_id)).first().path
        logging.getLogger("views-storage").info("THE ID IS %s, path is: %s" % (the_id, path))
        return path


stream = DynamicStorageDownloadView.as_view()
