from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^list/?$', views.list, name='list'),
    url(r'^watch/?$', views.watch, name='watch'),
    url(r'^camera/(?P<camera_name>.+)/?$', views.camera, name='camera')
#    url(r'^(?P<clip_id>\d+)/$', views.detail, name='detail'),
)
