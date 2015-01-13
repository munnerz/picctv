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
                                               "page_nav_range": page_nav_range
                                               })

def detail(request, clip_id):
    return render(request, 'clips/detail.html', {'clip_id': clip_id})

def analysis(request):
    return render(request, 'clips/analysis.html', {"data": models.analysis.objects[:30]})
