from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse

import models

def index(request):
    return render(request, 'clips/index.html', None)

def list(request):
    return render(request, 'clips/list.html', None)

def detail(request, clip_id):
    return render(request, 'clips/detail.html', {'clip_id': clip_id})

def analysis(request):
    return render(request, 'clips/analysis.html', {"data": models.analysis.objects[:30]})
