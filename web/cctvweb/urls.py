from django.conf.urls import patterns, include, url
from django.contrib import admin
import clips

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cctvweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^clips/', include('clips.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
