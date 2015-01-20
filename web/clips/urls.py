from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^list/?$', views.list, name='list'),
    url(r'^list/(?P<camera_name>.*)/$', views.list, name='list'),
    url(r'^watch/(?P<camera>.+)/(?P<time_start>.*)/$', views.watch, name='watch'),
    url(r'^analysis', views.analysis, name='analysis'),
    url(r'^(?P<clip_id>\d+)/$', views.detail, name='detail'),
)
