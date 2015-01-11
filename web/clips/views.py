from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

import models

def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def list(request, offset=0):
    return render(request, 'clips/list.html', {"cameras": models.clip.objects.distinct("camera_name"),
                                               "clips": models.clip.objects.order_by('-save_time').limit(50)
                                               })

def detail(request, clip_id):
    return render(request, 'clips/detail.html', {'clip_id': clip_id})

def analysis(request):
    return render(request, 'clips/analysis.html', {"data": models.analysis.objects[:30]})
