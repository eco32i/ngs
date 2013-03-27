from django.conf.urls import patterns, url
from django.views.generic.list import ListView

from cuff.models import ExpStat
from cuff import views

#
# URL scheme:
#   /exp/<exp_pk>/<track>/ - track base for exp
#   /exp/<exp_pk>/<track>/<data>/ - trac data for exp
#                                   `data`: data, replicates, count, diff

#   /exp/<exp_pk>/<dist>/ - distribution diff data for exp
#

urlpatterns = patterns('',
    # Home page - list of experiments
    # This view needs refactoring - it hits db too much.
    # Probably need to move run stats to its own table.
    url(r'^$', ListView.as_view(
        model=ExpStat,
        template_name='cuff/home.html'),
        name='cuff_home_view'),
    
    # Track urls
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/$', views.TrackView.as_view(),
        name='track_base_view'),
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/(?P<data>\w+)/$', views.TrackView.as_view(),
        name='track_data_view'),
)
