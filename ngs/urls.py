from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^cuff/', include('cuff.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

try:
    from local_urls import *
except:
    pass
