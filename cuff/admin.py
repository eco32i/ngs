from django.db import models
from django.contrib import admin

from cuff.models import (
    Gene, GeneCount, GeneData, GeneExpDiffData,
    GeneReplicateData, GeneFeature, Isoform, IsoformCount, IsoformData,
    IsoformExpDiffData, IsoformFeature, IsoformReplicateData,
    TSS, TSSCount, TSSData, TSSExpDiffData, TSSFeature, TSSReplicateData,
    CDS, CDSData, CDSCount,CDSExpDiffData, CDSFeature, CDSReplicateData,
    CDSDiffData, PromoterDiffData, SplicingDiffData, Sample, Replicate, 
    RunInfo
    )
    
admin.autodiscover()

class RunInfoAdmin(admin.ModelAdmin):
    model = RunInfo
    list_display = ('key', 'value',)
    
admin.site.register(RunInfo, RunInfoAdmin)

class ReplicateAdmin(admin.ModelAdmin):
    list_display = ('sample', 'replicate', 'file_name', 'total_mass',
        'norm_mass', 'internal_scale', 'external_scale',)
    raw_id_fields = ('sample',)
    
admin.site.register(Replicate, ReplicateAdmin)

BASE_TRACK_FIELDS = ('gene_short_name', 'locus', 'length', 'coverage')
BASE_DATA_FIELDS = ('sample', 'fpkm', 'conf_hi', 'conf_lo', 'status',)
BASE_COUNT_FIELDS = ('sample', 'count', 'variance', 'uncertainty', 'dispersion', 'status',)
BASE_DIFF_FIELDS = ('value_1', 'value_2', 'status', 'test_stat', 'p_value', 'q_value', 'significant',)
BASE_REPLICATE_FIELDS = ('sample', 'replicate', 'raw_frags', 'internal_scaled_frags', 'external_scaled_frags', 'fpkm', 'status',)

def rel_gene_short_name(obj):
    return obj.gene.gene_short_name
rel_gene_short_name.short_description = 'short name'

def tss_rel_gene_short_name(obj):
    return obj.tss_group.gene.gene_short_name
tss_rel_gene_short_name.short_description = 'short name'

def cds_rel_gene_short_name(obj):
    return obj.cds.gene.gene_short_name
cds_rel_gene_short_name.short_description = 'short name'

def cds_rel_tss_group_id(obj):
    return obj.cds.tss_group.tss_group_id
cds_rel_tss_group_id.short_description = 'TSS group id'

def isoform_rel_gene_short_name(obj):
    return obj.isoform.gene.gene_short_name
isoform_rel_gene_short_name.short_description = 'short name'

def isoform_rel_tss_group_id(obj):
    return obj.isoform.tss_group.tss_group_id
isoform_rel_tss_group_id.short_description = 'TSS group id'

def rel_gene_id(obj):
    return obj.gene.gene_id
rel_gene_id.short_description = 'gene id'

def rel_tss_group_id(obj):
    return obj.tss_group.tss_group_id
rel_tss_group_id.short_description = 'TSS group id'

def rel_cds_id(obj):
    return obj.cds.cds_id
rel_gene_id.short_description = 'CDS id'

def rel_isoform_id(obj):
    return obj.isoform.isoform_id
rel_gene_id.short_description = 'Isoform id'

#
# Gene track admin
#
class GeneAdmin(admin.ModelAdmin):
    list_display = BASE_TRACK_FIELDS + ('gene_id',)
    search_fields = ('gene_short_name',)

class GeneAdmin(admin.ModelAdmin):
    list_display = BASE_TRACK_FIELDS + ('gene_id',)
    search_fields = ('gene_short_name',)

admin.site.register(Gene, GeneAdmin)

class GeneDataAdmin(admin.ModelAdmin):
    list_display = BASE_DATA_FIELDS + (rel_gene_id, rel_gene_short_name,)
    list_filter = ('sample', 'status',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('gene', 'sample',)
    
admin.site.register(GeneData, GeneDataAdmin)

class GeneCountAdmin(admin.ModelAdmin):
    list_display = BASE_COUNT_FIELDS + (rel_gene_id, rel_gene_short_name,)
    list_filter = ('sample', 'status',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('gene', 'sample',)
    
admin.site.register(GeneCount, GeneCountAdmin)

class GeneExpDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_gene_id, rel_gene_short_name,) + BASE_DIFF_FIELDS + ('log2_fold_change',)
    list_filter = ('status', 'significant',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('gene',)
    
admin.site.register(GeneExpDiffData, GeneExpDiffDataAdmin)

class GeneReplicateDataAdmin(admin.ModelAdmin):
    list_display = BASE_REPLICATE_FIELDS + (rel_gene_id,)
    list_filter = ('sample', 'status',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('gene', 'sample',)
    
admin.site.register(GeneReplicateData, GeneReplicateDataAdmin)

#
# TSS track admin
#
class TSSAdmin(admin.ModelAdmin):
    list_display = BASE_TRACK_FIELDS + (rel_gene_id, 'tss_group_id',)
    search_fields = ('gene__gene_short_name',)
    
admin.site.register(TSS, TSSAdmin)

class TSSDataAdmin(admin.ModelAdmin):
    list_display = (rel_tss_group_id, tss_rel_gene_short_name) + BASE_DATA_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('tss_group__gene__gene_short_name',)
    raw_id_fields = ('tss_group', 'sample',)

admin.site.register(TSSData, TSSDataAdmin)

class TSSCountAdmin(admin.ModelAdmin):
    list_display = (rel_tss_group_id, tss_rel_gene_short_name,) + BASE_COUNT_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('tss_group__gene__gene_short_name',)
    raw_id_fields = ('tss_group', 'sample',)
    
admin.site.register(TSSCount, TSSCountAdmin)

class TSSExpDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_tss_group_id, tss_rel_gene_short_name,) + BASE_DIFF_FIELDS + ('log2_fold_change',)
    list_filter = ('status', 'significant',)
    search_fields = ('tss_group__gene__gene_short_name',)
    raw_id_fields = ('tss_group',)
    
admin.site.register(TSSExpDiffData, TSSExpDiffDataAdmin)

class TSSReplicateDataAdmin(admin.ModelAdmin):
    list_display = BASE_REPLICATE_FIELDS + (rel_tss_group_id,)
    list_filter = ('sample', 'status',)
    search_fields = ('tss_group__gene__gene_short_name',)
    raw_id_fields = ('tss_group', 'sample',)
    
admin.site.register(TSSReplicateData, TSSReplicateDataAdmin)

#
# CDS track admin
#
class CDSAdmin(admin.ModelAdmin):
    list_display = BASE_TRACK_FIELDS + (rel_gene_id, rel_tss_group_id, 'cds_id',)
    search_fields = ('gene__gene_short_name',)
    
admin.site.register(CDS, CDSAdmin)

class CDSDataAdmin(admin.ModelAdmin):
    list_display = (rel_cds_id, cds_rel_tss_group_id, cds_rel_gene_short_name) + BASE_DATA_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('cds__gene__gene_short_name',)
    raw_id_fields = ('cds', 'sample',)

admin.site.register(CDSData, CDSDataAdmin)

class CDSCountAdmin(admin.ModelAdmin):
    list_display = (rel_cds_id, cds_rel_tss_group_id, cds_rel_gene_short_name,) + BASE_COUNT_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('cds__gene__gene_short_name',)
    raw_id_fields = ('cds', 'sample',)
    
admin.site.register(CDSCount, CDSCountAdmin)

class CDSExpDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_cds_id, cds_rel_tss_group_id, cds_rel_gene_short_name,) + BASE_DIFF_FIELDS + ('log2_fold_change',)
    list_filter = ('status', 'significant',)
    search_fields = ('cds__gene__gene_short_name',)
    raw_id_fields = ('cds',)
    
admin.site.register(CDSExpDiffData, CDSExpDiffDataAdmin)

class CDSReplicateDataAdmin(admin.ModelAdmin):
    list_display = BASE_REPLICATE_FIELDS + (rel_cds_id,)
    list_filter = ('sample', 'status',)
    search_fields = ('cds__gene__gene_short_name',)
    raw_id_fields = ('cds', 'sample',)
    
admin.site.register(CDSReplicateData, CDSReplicateDataAdmin)

#
# Isoform track admin
#
class IsoformAdmin(admin.ModelAdmin):
    list_display = BASE_TRACK_FIELDS + (rel_gene_id, rel_tss_group_id, 'isoform_id',)
    search_fields = ('gene__gene_short_name',)
    
admin.site.register(Isoform, IsoformAdmin)

class IsoformDataAdmin(admin.ModelAdmin):
    list_display = (rel_isoform_id, isoform_rel_tss_group_id, isoform_rel_gene_short_name) + BASE_DATA_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('isoform__gene__gene_short_name',)
    raw_id_fields = ('isoform', 'sample',)

admin.site.register(IsoformData, IsoformDataAdmin)

class IsoformCountAdmin(admin.ModelAdmin):
    list_display = (rel_isoform_id, isoform_rel_tss_group_id, isoform_rel_gene_short_name,) + BASE_COUNT_FIELDS
    list_filter = ('sample', 'status',)
    search_fields = ('isoform__gene__gene_short_name',)
    raw_id_fields = ('isoform', 'sample',)
    
admin.site.register(IsoformCount, IsoformCountAdmin)

class IsoformExpDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_isoform_id, isoform_rel_tss_group_id, isoform_rel_gene_short_name,) + BASE_DIFF_FIELDS + ('log2_fold_change',)
    list_filter = ('status', 'significant',)
    search_fields = ('isoform__gene__gene_short_name',)
    raw_id_fields = ('isoform',)
    
admin.site.register(IsoformExpDiffData, IsoformExpDiffDataAdmin)

class IsoformReplicateDataAdmin(admin.ModelAdmin):
    list_display = BASE_REPLICATE_FIELDS + (rel_isoform_id,)
    list_filter = ('sample', 'status',)
    search_fields = ('isoform__gene__gene_short_name',)
    raw_id_fields = ('isoform', 'sample',)

admin.site.register(IsoformReplicateData, IsoformReplicateDataAdmin)

#
# Dist level admin
#

class PromoterDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_gene_id, rel_gene_short_name,) + BASE_DIFF_FIELDS + ('js_dist',)
    list_filter = ('status', 'significant',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('gene',)
    
admin.site.register(PromoterDiffData, PromoterDiffDataAdmin)

class SplicingDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_tss_group_id, tss_rel_gene_short_name,) + BASE_DIFF_FIELDS + ('js_dist',)
    list_filter = ('status', 'significant',)
    search_fields = ('gene__gene_short_name',)
    raw_id_fields = ('tss_group',)
    
admin.site.register(SplicingDiffData, SplicingDiffDataAdmin)

class CDSDiffDataAdmin(admin.ModelAdmin):
    list_display = (rel_cds_id, cds_rel_gene_short_name,) + BASE_DIFF_FIELDS + ('js_dist',)
    list_filter = ('status', 'significant',)
    search_fields = ('cds__gene_short_name',)
    raw_id_fields = ('gene',)
    
admin.site.register(CDSDiffData, CDSDiffDataAdmin)
