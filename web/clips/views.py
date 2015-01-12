from django.shortcuts import render
from django.core.paginator import Paginator
from django.template import RequestContext, loader
from django.http import HttpResponse

import models

def index(request):
    return render(request, 'clips/index.html', {"logs": models.logmsg.objects.order_by('-save_time').limit(50)})

def list(request, camera_name=''):
    page = int(request.GET.get('p', 1))
    limit = int(request.GET.get('l', 15))
    offset = int((page - 1) * limit)
    paginator = Paginator(models.clip.objects.filter(camera_name=camera_name).order_by('end_item').skip(offset), limit)
    return render(request, 'clips/list.html', {"cameras": models.clip.objects.distinct("camera_name"),
                                               "all_clips": models.clip.objects.order_by('end_time'),
                                               "camera_name": camera_name,
                                               "page_num": page,
                                               "paginator": paginator,
                                               "camera_clips": paginator.page(page)
                                               })

def detail(request, clip_id):
    return render(request, 'clips/detail.html', {'clip_id': clip_id})

def analysis(request):
    return render(request, 'clips/analysis.html', {"data": models.analysis.objects[:30]})
