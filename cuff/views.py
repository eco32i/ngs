from django.db import models
from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import View, FormView
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.edit import BaseFormView
from django.utils.encoding import smart_str
from django.utils.text import capfirst

from cuff.models import Experiment
#~ from cuff.models import (RunInfo, Replicate, Sample, Gene, Isoform,
    #~ TSS, CDS, PromoterDiffData, SplicingDiffData, CDSDiffData)
#~ from cuff.forms import GeneFilterForm

ALLOWED_LOOKUPS = ('iexact', 'icontains', 'in', 'gt', 'gte', 'lt',
    'lte', 'istratswith', 'iendswith', 'range', 'isnull', 'iregex')

#~ class HomeView(ListView):
    #~ model = RunInfo
    #~ template_name = 'cuff/home.html'
    #~ 
    #~ def get_context_data(self, **kwargs):
        #~ context = super(HomeView, self).get_context_data(**kwargs)
        #~ stat_dict = {
            #~ 'samples': Sample.objects.count(),
            #~ 'genes': Gene.objects.count(),
            #~ 'isoforms': Isoform.objects.count(),
            #~ 'TSS': TSS.objects.count(),
            #~ 'CDS': CDS.objects.count(),
            #~ 'promoters': PromoterDiffData.objects.count(),
            #~ 'splicing': SplicingDiffData.objects.count(),
            #~ 'relCDS': CDSDiffData.objects.count(),
            #~ }
        #~ context['stat'] = stat_dict
        #~ context['samples'] = Sample.objects.values_list('sample_name', flat=True)
        #~ return context


class TrackView(ListView):
    template_name = 'cuff/track.html'
    
    def __init__(self, **kwargs):
        super(TrackView, self).__init__(**kwargs)
        # These two should go to `self.get` probably
        self.filters = kwargs.get('filters', {})
        self.ordering = kwargs.get('order', [])
        
    def _get_filters(self, request):
        params = request.GET.copy()
        params.pop('page', None)
        params.pop('_filter', None)
        # TODO: Factor ordering out to `self.get_ordering()`
        self.ordering = params.pop('o', [])
        opts = self.model._meta
        filters = {}
        for k,v in params.items():
            if not v:
                continue
            try:
                field, lookup = k.split('__')
                if lookup in ALLOWED_LOOKUPS:
                    filters.update({smart_str(k): v,})
                elif field in opts.get_all_field_names():
                    filters.update({smart_str('%s__icontains' % k): v,})
            except ValueError:
                filters.update({smart_str('%s__icontains' % k): v,})
        return filters

    def get_queryset(self):
        qs = self.model._default_manager.for_exp(self.exp)
        return qs.filter(**self.filters).order_by(*self.ordering)
    
    def get_form(self):
        if self.form_class:
            return self.form_class()
        else:
            return None


    def get_context_data(self,  **kwargs):
        context = super(TrackView, self).get_context_data(**kwargs)
        opts = self.model._meta
        context.update({
            'filters': self.filters,
            'model': self.model,
            'fields': opts.list_display,
            'form': self.get_form(),
            })
        return context

    def _set_options(self):
        self.exp = get_object_or_404(Experiment, pk=int(self.kwargs.get('exp_pk', '')))
        track_base = self.kwargs['track']
        track_data = self.kwargs.get('data', '')
        if track_base in ['cds', 'tss']:
            # We need proper capitalization to get the form class later
            track_base = track_base.upper()
        if track_base in ['promoter', 'splicing', 'relcds']:
            track_model = '{base}diffdata'.format(base=track_base)
            track_form_class = '{base}DiffDataFilterForm'.format(base=capfirst(track_base))
        elif track_data in ['data', 'count']:
            track_model = '{base}{data}'.format(base=track_base,data=track_data)
            track_form_class = '{base}{data}FilterForm'.format(
                base=capfirst(track_base),
                data=capfirst(track_data))
        elif track_data == 'replicate':
            track_model = '{base}replicatedata'.format(base=track_base)
            track_form_class = '{base}ReplicateDataFilterForm'.format(
                base=capfirst(track_base))
        elif track_data == 'diff':
            track_model = '{base}expdiffdata'.format(base=track_base)
            track_form_class = '{base}ExpDiffDataFilterForm'.format(
                base=capfirst(track_base))
        else:
            track_model = track_base
            track_form_class = '{base}FilterForm'.format(base=capfirst(track_base))
        try:
            from cuff import forms as cf
            self.form_class = getattr(cf, track_form_class)
        except AttributeError:
            self.form_class = None
        # TODO: Need to get rid of hardcoded app name!
        self.model = get_model('cuff', track_model)
        
        
    def get(self, request, *args, **kwargs):
        # get takes care of initial display and ordering
        self._set_options()
        if '_clear' in request.GET:
            self.filters.clear()
            self.ordering = []
        else:
            filters = self._get_filters(request)
            self.filters.update(filters)
            #self.ordering = self._get_ordering(request)
        return super(TrackView, self).get(request, *args, **kwargs)
