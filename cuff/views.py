from django.db import models
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import View, FormView
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.edit import BaseFormView
from django.utils.encoding import smart_str

from cuff.models import (RunInfo, Replicate, Sample, Gene, Isoform,
    TSS, CDS, PromoterDiffData, SplicingDiffData, CDSDiffData)
from cuff.forms import GeneFilterForm

ALLOWED_LOOKUPS = ('iexact', 'icontains', 'in', 'gt', 'gte', 'lt',
    'lte', 'istratswith', 'iendswith', 'range', 'isnull', 'iregex')

class HomeView(ListView):
    model = RunInfo
    template_name = 'cuff/home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        stat_dict = {
            'samples': Sample.objects.count(),
            'genes': Gene.objects.count(),
            'isoforms': Isoform.objects.count(),
            'TSS': TSS.objects.count(),
            'CDS': CDS.objects.count(),
            'promoters': PromoterDiffData.objects.count(),
            'splicing': SplicingDiffData.objects.count(),
            'relCDS': CDSDiffData.objects.count(),
            }
        context['stat'] = stat_dict
        context['samples'] = Sample.objects.values_list('sample_name', flat=True)
        return context


class FilteredTrackView(ListView, BaseFormView):
    
    def __init__(self, **kwargs):
        super(FilteredTrackView, self).__init__(**kwargs)
        self.filters = kwargs.get('filters', {})
        # TODO: Get default ordering from the model's opts
        self.ordering = kwargs.get('order', [])
    
    def _get_filters(self, request):
        params = request.GET.copy()
        params.pop('page', None)
        params.pop('_filter', None)
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
        qs = super(FilteredTrackView, self).get_queryset()
        return qs.filter(**self.filters).order_by(*self.ordering)
    
    def get_context_data(self,  **kwargs):
        context = super(FilteredTrackView, self).get_context_data(**kwargs)
        context.update({'form': self.get_form(self.form_class),})
        return context
        
    def get(self, request, *args, **kwargs):
        # get takes care of initial display and ordering
        if '_clear' in request.GET:
            self.filters.clear()
            self.ordering = []
        else:
            filters = self._get_filters(request)
            self.filters.update(filters)
            #self.ordering = self._get_ordering(request)
        return super(FilteredTrackView, self).get(request, *args, **kwargs)
