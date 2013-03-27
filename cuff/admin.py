from django.contrib import admin

from cuff.models import Replicate, RunInfo, Experiment, ExpStat

admin.autodiscover()

class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('run_date', 'analysis_date', 'title', 'species',
        'library', 'description')
    date_hierarchy = 'run_date'
    list_filter = ('species', 'library',)

admin.site.register(Experiment, ExperimentAdmin)

class RunInfoAdmin(admin.ModelAdmin):
    model = RunInfo
    list_display = ('key', 'value',)
    list_filter = ('experiment',)
    
admin.site.register(RunInfo, RunInfoAdmin)

class ReplicateAdmin(admin.ModelAdmin):
    list_display = ('sample', 'replicate', 'file_name', 'total_mass',
        'norm_mass', 'internal_scale', 'external_scale',)
    raw_id_fields = ('sample',)
    list_filter = ('sample__experiment',)
    
admin.site.register(Replicate, ReplicateAdmin)

class ExpStatAdmin(admin.ModelAdmin):
    model = ExpStat
    list_display = ('gene_count', 'promoter_count', 'tss_count', 
        'splicing_count', 'isoform_count', 'cds_count', 'relcds_count',)

admin.site.register(ExpStat, ExpStatAdmin)
