from django.conf.urls import patterns, url

from cuff import views

#
# URL scheme:
#   /exp/<exp_pk>/<track>/ - track base for exp
#   /exp/<exp_pk>/<track>/<data>/ - trac data for exp
#                                   `data`: data, replicates, count, diff

#   /exp/<exp_pk>/<dist>/ - distribution diff data for exp
#

urlpatterns = patterns('',
    # url(r'^$', views.HomeView.as_view(), name='cuff_home_view'),
    
    # Track urls
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/$', views.TrackView.as_view(),
        name='track_base_view'),
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/(?P<data>\w+)/$', views.TrackView.as_view(),
        name='track_data_view'),
)
