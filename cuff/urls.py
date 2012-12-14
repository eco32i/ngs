from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from cuff import views
from cuff.models import (RunInfo, Gene, GeneData, GeneReplicateData, 
    GeneExpDiffData, GeneCount, TSS, TSSData, TSSCount, TSSReplicateData,
    TSSExpDiffData, Isoform, IsoformData, IsoformCount, IsoformReplicateData,
    IsoformExpDiffData, CDS, CDSData, CDSCount, CDSReplicateData,
    CDSExpDiffData, PromoterDiffData, SplicingDiffData, CDSDiffData)
from cuff.forms import  (GeneFilterForm, GeneDataFilterForm, GeneCountFilterForm, 
    GeneReplicateDataFilterForm, GeneExpDiffDataFilterForm, 
    TSSFilterForm, TSSDataFilterForm, TSSCountFilterForm, TSSReplicateDataFilterForm,
    TSSExpDiffDataFilterForm, IsoformFilterForm, IsoformDataFilterForm, 
    IsoformCountFilterForm, IsoformReplicateDataFilterForm, IsoformExpDiffDataFilterForm,
    CDSFilterForm, CDSDataFilterForm, CDSCountFilterForm, CDSReplicateDataFilterForm,
    CDSExpDiffDataFilterForm)

urlpatterns = patterns('',
    url(r'^$', views.HomeView.as_view(), name='cuff_home_view'),
    
    # Gene track
    url(r'^gene/$', views.FilteredTrackView.as_view(
        model=Gene,
        template_name='cuff/genes.html',
        form_class=GeneFilterForm), name='cuff_gene_view'),
    url(r'^gene/data/$', views.FilteredTrackView.as_view(
        model=GeneData,
        template_name='cuff/gene_data.html',
        form_class=GeneDataFilterForm), name='cuff_genedata_view'),
    url(r'^gene/replicates/$', views.FilteredTrackView.as_view(
        model=GeneReplicateData,
        template_name='cuff/gene_replicates.html',
        form_class=GeneReplicateDataFilterForm), name='cuff_genereplicates_view'),
    url(r'^gene/count/$', views.FilteredTrackView.as_view(
        model=GeneCount,
        template_name='cuff/gene_counts.html',
        form_class=GeneCountFilterForm), name='cuff_genecounts_view'),
    url(r'^gene/diff/$', views.FilteredTrackView.as_view(
        model=GeneExpDiffData,
        template_name='cuff/gene_geneexpdiffdata.html',
        form_class=GeneExpDiffDataFilterForm), name='cuff_geneexpdiffdata_view'),
    
    # TSS group track
    url(r'^tss/$', views.FilteredTrackView.as_view(
        model=TSS,
        template_name='cuff/tss_groups.html',
        form_class=TSSFilterForm), name='cuff_tss_view'),
    url(r'^tss/data/$', views.FilteredTrackView.as_view(
        model=TSSData,
        template_name='cuff/tss_data.html',
        form_class=TSSDataFilterForm), name='cuff_tssdata_view'),
    url(r'^tss/count/$', views.FilteredTrackView.as_view(
        model=TSSCount,
        template_name='cuff/tss_counts.html',
        form_class=TSSCountFilterForm), name='cuff_tsscounts_view'),
    url(r'^tss/replicates/$', views.FilteredTrackView.as_view(
        model=TSSReplicateData,
        template_name='cuff/tss_replicates.html',
        form_class=TSSReplicateDataFilterForm), name='cuff_tssreplicates_view'),
    url(r'^tss/diff/$', views.FilteredTrackView.as_view(
        model=TSSExpDiffData,
        template_name='cuff/tss_tssexpdiffdata.html',
        form_class=TSSExpDiffDataFilterForm), name='cuff_tssexpdiffdata_view'),
    
    # Isoform track
    url(r'^isoform/$', views.FilteredTrackView.as_view(
        model=Isoform,
        template_name='cuff/isoforms.html',
        form_class=IsoformFilterForm), name='cuff_isoform_view'),
    url(r'^isoform/data/$', views.FilteredTrackView.as_view(
        model=IsoformData,
        template_name='cuff/isoform_data.html',
        form_class=IsoformDataFilterForm), name='cuff_isoformdata_view'),
    url(r'^isoform/count/$', views.FilteredTrackView.as_view(
        model=IsoformCount,
        template_name='cuff/isoform_counts.html',
        form_class=IsoformCountFilterForm), name='cuff_isoformcounts_view'),
    url(r'^isoform/replicates/$', views.FilteredTrackView.as_view(
        model=IsoformReplicateData,
        template_name='cuff/isoform_replicates.html',
        form_class=IsoformReplicateDataFilterForm), name='cuff_isoformreplicates_view'),
    url(r'^isoform/diff/$', views.FilteredTrackView.as_view(
        model=IsoformExpDiffData,
        template_name='cuff/isoform_expdiffdata.html',
        form_class=IsoformExpDiffDataFilterForm), name='cuff_isoformexpdiffdata_view'),
    
    # CDS track
    url(r'^cds/$', views.FilteredTrackView.as_view(
        model=CDS,
        template_name='cuff/cdss.html',
        form_class=CDSFilterForm), name='cuff_cds_view'),
    url(r'^cds/data/$', views.FilteredTrackView.as_view(
        model=CDSData,
        template_name='cuff/cds_data.html',
        form_class=CDSDataFilterForm), name='cuff_cdsdata_view'),
    url(r'^cds/count/$', views.FilteredTrackView.as_view(
        model=CDSCount,
        template_name='cuff/cds_counts.html',
        form_class=CDSCountFilterForm), name='cuff_cdscounts_view'),
    url(r'^cds/replicates/$', views.FilteredTrackView.as_view(
        model=CDSReplicateData,
        template_name='cuff/cds_replicates.html',
        form_class=CDSReplicateDataFilterForm), name='cuff_cdsreplicates_view'),
    url(r'^cds/diff/$', views.FilteredTrackView.as_view(
        model=CDSExpDiffData,
        template_name='cuff/cds_expdiffdata.html',
        form_class=CDSExpDiffDataFilterForm), name='cuff_cdsexpdiffdata_view'),
        
    # Distributions
    url(r'^promoters/$', views.FilteredTrackView.as_view(
        model=PromoterDiffData,
        template_name='cuff/promoters.html',
        form_class=GeneExpDiffDataFilterForm), name='cuff_promoters_view'),
    url(r'^splicing/$', views.FilteredTrackView.as_view(
        model=SplicingDiffData,
        template_name='cuff/splicing.html',
        form_class=TSSExpDiffDataFilterForm), name='cuff_splicing_view'),
    url(r'^relcds/$', views.FilteredTrackView.as_view(
        model=CDSDiffData,
        template_name='cuff/promoters.html',
        form_class=GeneExpDiffDataFilterForm), name='cuff_relcds_view'),
)

urlpatterns += staticfiles_urlpatterns()
