import math
import numpy as np
import pandas as pd

from pylab import figure, plot
from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt

from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from cuff.models import Experiment
from plot.ggstyle import rstyle


class PlotMixin(object):
    '''
    A mixin that allows matplotlib plotting. Should be used together
    with ListView or DetailView subclasses to get the plotting data
    from the database.
    '''
    format = None

    def make_plot(self):
        '''
        This needs to be implemented in the subclass.
        '''
        pass
    
    def style_plot(self, axes):
        '''
        By default does nothing. May be used to style the plot
        (xkcd, ggplot2, etc).
        '''
        pass
    
    def get_response_content_type(self):
        '''
        Returns plot format to be used in the response.
        '''
        if self.format is not None:
            return 'image/{0}'.format(self.format)
        else:
            raise ImproperlyConfigured('No format is specified for the plot')
        
        
    def render_to_plot(self, context, **response_kwargs):
        response = HttpResponse(
            content_type=self.get_response_content_type()
            )
        fig = self.make_plot()
        fig.savefig(response, format=self.format)
        return response


class QuerysetPlotView(ListView, PlotMixin):
    '''
    A view that plots data from a queryset.
    '''
    data_fields = None
    
    def _get_model_from_track(self):
        return get_model('cuff', self.kwargs['track'])
        
    def get_queryset(self):
        self.model = self._get_model_from_track()
        self.exp = get_object_or_404(Experiment, pk=int(self.kwargs.get('exp_pk', '')))
        return self.model._default_manager.for_exp(self.exp)
        
    def get_dataframe(self, sample=None):
        '''
        Builds a pandas dataframe by retrieving the fields specified
        in self.data_fields from self.queryset.
        '''
        opts = self.model._meta
        fields = [f for f in opts.get_all_field_names() if f in self.data_fields]
        if sample is None:
            values_dict = self.object_list.values(*fields)
        else:
            values_dict = self.object_list.filter(sample=sample).values(*fields)
        df = pd.DataFrame.from_records(values_dict)
        return df
        
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_plot(context, **response_kwargs)


class VolcanoPlotView(QuerysetPlotView):
    data_fields = ['log2_fold_change', 'p_value', 'significant',]
    format = 'png'
    
    def _get_model_from_track(self):
        # FIXME: Needs to be fixed for distribution level data
        track = self.kwargs['track']
        return get_model('cuff', '{0}ExpDiffData'.format(track))
    
    def make_plot(self):
        df = self.get_dataframe()
        df = df[df['p_value'] > 0]
        df['p_value'] = -1 * df['p_value'].map(math.log10)
        # We need this (arbitrary) cutoff to avoid
        # ValueError from NaN to int conversion
        df = df[df['log2_fold_change'] < 100]
        df = df[df['log2_fold_change'] > -100]
        fig = plt.figure()
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        
        ax.legend()
        ax.set_xlabel('log$_{2}$(fold change)')
        ax.set_ylabel('-log$_{10}$(p value)')
        ax.title.set_fontsize(18)
        df_sig = df[df['significant'] == 'yes']
        df_nonsig = df[df['significant'] == 'no']
        
        # colors = np.where(df['significant'] == 'yes', 'r', 'b')
        # ax.plot(df['log2_fold_change'], df['p_value'], 'o', color='#268bd2', alpha=0.2)
        ax.plot(df_sig['log2_fold_change'], df_sig['p_value'], 'o',
            color='#cb4b16',
            label='significant',
            alpha=0.45)
        ax.plot(df_nonsig['log2_fold_change'], df_nonsig['p_value'], 'o',
            color='#268bd2',
            label='not significant',
            alpha=0.2)
        ax.legend()
        rstyle(ax)
        return fig


class DensityPlotView(QuerysetPlotView):
    data_fields = ['fpkm',]
    format = 'png'
    
    def _get_model_from_track(self):
        return get_model('cuff', '{0}Data'.format(self.kwargs['track']))
        
    def make_plot(self):
        c_map = ['#268bd2', '#cb4b16',]
        fig = plt.figure()
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        
        ax.set_xlabel('log$_{10}$(FPKM+1)')
        ax.set_ylabel('Density')
        ax.title.set_fontsize(18)
        
        for i,sample in enumerate(self.exp.sample_set.all()):
            df = self.get_dataframe(sample)[self.data_fields[0]] + 1
            df = df.map(math.log10)
            base = np.linspace(0, max(df), 100)
            kde = gaussian_kde(df)
            kde_pdf = kde.evaluate(base)
            ax.plot(base, kde_pdf,
                color=c_map[i],
                label=sample.sample_name,
                alpha=0.8)
            ax.fill_between(base, kde_pdf, color=c_map[i], alpha=0.4)
        ax.legend()
        rstyle(ax)
        return fig


class DispersionPlotView(QuerysetPlotView):
    data_fields = ['count', 'dispersion',]
    format = 'png'
    
    def _get_model_from_track(self):
        return get_model('cuff', '{0}Count'.format(self.kwargs['track']))
    
    def get_queryset(self):
        qs = super(DispersionPlotView, self).get_queryset()
        self.num_samples = self.exp.sample_set.count()
        self.sample_names = self.exp.sample_set.values_list('sample_name', flat=True)
        return qs
        
    def make_plot(self):
        fig = plt.figure(figsize=(10,5))
        fig.patch.set_alpha(0)
        for i,sample in enumerate(self.exp.sample_set.all()):
            df = self.get_dataframe(sample)
            ax = fig.add_subplot(1,self.num_samples,i,adjustable='datalim',aspect='equal')
            ax.plot(df['count']+1, df['dispersion']+1, 'o', color='#268bd2', alpha=0.2)
            ax.set_title(sample.sample_name)
            ax.set_xlabel('Count')
            ax.set_ylabel('Dispersion')
            ax.set_xscale('log')
            ax.set_yscale('log')
            rstyle(ax)
        
        return fig
