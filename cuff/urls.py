from django.conf.urls import patterns, url
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required

from cuff.models import ExpStat
from cuff import views
from plot import views as plt_views

#
# URL scheme:
#   /exp/<exp_pk>/<track>/ - track base for exp
#   /exp/density/<exp_pk>/<track>/ - density plot for the track in exp
#   /exp/<exp_pk>/<track>/<data>/ - trac data for exp
#                                   `data`: data, replicates, count, diff

#   /exp/<exp_pk>/<dist>/ - distribution diff data for exp
#

urlpatterns = patterns('',
    # Home page - list of experiments
    url(r'^$', login_required(ListView.as_view(
        model=ExpStat,
        template_name='cuff/home.html')),
        name='cuff_home_view'),
    # Track urls
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(views.TrackView.as_view()),
        name='track_base_view'),
    url(r'^exp/(?P<exp_pk>\d+)/(?P<track>\w+)/(?P<data>\w+)/$', login_required(views.TrackView.as_view()),
        name='track_data_view'),
    # Plot urls
    # TODO: put the plots into some key:value store (redis?) for fast
    # retrieval until this whole thing is ported to Bokeh.
    
    # Track level plots: density, dispersion, SCV, (volcano?)
    #url(r'^exp/plot/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(plt_views.DensityPlotView.as_view()),
    #    name='density_plot_view'),
    url(r'^plots/exp/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(views.TrackPlotsView.as_view()),
        name='track_plots_view'),
        
    url(r'^exp/density/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(plt_views.DensityPlotView.as_view()),
        name='density_plot_view'),
    url(r'^exp/dispersion/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(plt_views.DispersionPlotView.as_view()),
        name='dispersion_plot_view'),
    url(r'^exp/volcano/(?P<exp_pk>\d+)/(?P<track>\w+)/$', login_required(plt_views.VolcanoPlotView.as_view()),
        name='volcano_plot_view'),
        
)
