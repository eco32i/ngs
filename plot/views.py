import math, sys
import numpy as np
import pandas as pd
import brewer2mpl

from pylab import figure, plot
from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt

from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured, FieldError
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


class BarPlotView(QuerysetPlotView):
    data_fields = ['fpkm', 'sample', 'conf_hi', 'conf_lo',]
    format = 'png'
    pk_list = None
    
    def _get_model_from_track(self):
        track = self.kwargs['track']
        return get_model('cuff', '{0}Data'.format(track))
    
    def _get_gene_short_names(self):
        gene_name_field = 'gene__gene_short_name'
        track = self.kwargs['track'].lower()
        if track == 'tss':
            gene_name_field = 'tss_group__{0}'.format(gene_name_field)
        elif track != 'gene':
            gene_name_field = '{0}__{1}'.format(track, gene_name_field)
        return self.object_list.values_list(gene_name_field, flat=True)
    
    def get_queryset(self):
        qs = super(BarPlotView, self).get_queryset()
        if self.pk_list:
            return qs.filter(pk__in=self.pk_list)
        else:
            return qs
    
    def get(self, request, *args, **kwargs):
        gene_pks = request.GET.get('genes')
        self.pk_list = [int(x) for x in gene_pks.split(',')]
        return super(BarPlotView, self).get(request, *args, **kwargs)
    
    def make_plot(self):
        fig = plt.figure()
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        ax.set_xlabel('Genes')
        ax.set_ylabel('FPKM')
        ax.title.set_fontsize(18)
        
        cmap = brewer2mpl.get_map('Set2', 'qualitative', 8).mpl_colors
        
        gene_names = self._get_gene_short_names()
        num_exp = self.exp.sample_set.count()
        bar_width = 1. / num_exp
        
        
        # We plot separately for each sample in the experiment
        for i,sample in enumerate(self.exp.sample_set.all()):
            df = self.get_dataframe(sample=sample)
            index = np.arange(df.shape[0])
            ax.bar(index + i*bar_width, df['fpkm'],
                width=bar_width,
                yerr=[df['fpkm']-df['conf_lo'], df['conf_hi']-df['fpkm']],
                error_kw={'ecolor': cmap[i],},
                label=sample.sample_name,
                color=cmap[i],
                edgecolor=cmap[i],
                alpha=0.45)
        
        plt.xticks(np.arange(self.object_list.count() // num_exp),
            [name for i,name in enumerate(gene_names) if i % num_exp == 0])
        plt.legend()
        plt.tight_layout()
        rstyle(ax)
        return fig
        
        
class VolcanoPlotView(QuerysetPlotView):
    data_fields = ['log2_fold_change', 'js_dist', 'p_value', 'q_value']
    format = 'png'
    alpha = 0.05
    
    def _get_model_from_track(self):
        track = self.kwargs['track']
        if track in ['splicing', 'promoter', 'relcds']:
            diff_data = 'DiffData'
        else:
            diff_data = 'ExpDiffData'
        return get_model('cuff', '{0}{1}'.format(track, diff_data))

    def make_plot(self):
        if self.kwargs['track'] in ['splicing', 'promoter', 'relcds']:
            x_field = 'js_dist'
        else:
            x_field = 'log2_fold_change'
        df = self.get_dataframe()
        df = df[df['p_value'] > 0]
        df['p_value'] = -1 * df['p_value'].map(math.log10)
        # This is somewhat arbitrary
        max_ = sys.float_info.max * 0.1
        df = df[df[x_field] < max_]
        df = df[df[x_field] > -max_]
        fig = plt.figure()
        fig.patch.set_alpha(0)
        ax = fig.add_subplot(111)
        
        ax.set_xlabel('log$_{2}$(fold change)')
        ax.set_ylabel('-log$_{10}$(p value)')
        ax.title.set_fontsize(18)
        df_sig = df[df['q_value'] <= self.alpha]
        df_nonsig = df[df['q_value'] > self.alpha]
        
        ax.plot(df_sig[x_field], df_sig['p_value'], 'o',
            color='#cb4b16',
            label='significant',
            alpha=0.45)
        ax.plot(df_nonsig[x_field], df_nonsig['p_value'], 'o',
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
        
        ax.set_xlabel('log$_{10}$(FPKM)')
        ax.set_ylabel('Density')
        ax.title.set_fontsize(18)
        
        for i,sample in enumerate(self.exp.sample_set.all()):
            df = self.get_dataframe(sample)[self.data_fields[0]]
            df = df[df > 0]
            df = df.map(math.log10)
            base = np.linspace(min(df), max(df), 200)
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
