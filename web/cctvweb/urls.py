from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
import clips

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cctvweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^clips/', include('clips.urls')),
    url(r'^$', lambda r: HttpResponseRedirect('clips/')),
    url(r'^admin/', include(admin.site.urls)),
)
