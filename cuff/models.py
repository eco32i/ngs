from django.db import models
from django.db.models import options

'''
cummerbund schema:
SQL models for Tophat/Cufflinks pipeline results access.

Data file parsing order:
    - RunInfo file
        run.info
        Read whatever key:value pairs are present in the tab-delimited file
    - Replicates
        read_groups.info
        replicate names (rep_name) are concatenated from condition and
        replicate number
    - Genes
        -- Gene
            genes.fpkm_tracking
            Populate Gene table with appropriate fields from fpkm file
        -- GeneData
            genes.fpkm_tracking
        -- GeneExpDiffData
            gene_exp.diff
        -- PromoterDiffData
            promoters.diff
        -- GeneCount
            genes.count_tracking
        -- GeneReplicateData
            ... currently missing
    - Isoforms
        -- Isoform
        -- IsoformData
        -- IsoformExpDiffData
        -- IsoformCount
        -- IsoformReplicateData
    - TSS groups
        -- TSS
        -- TSSData
        -- TSSExpDiffData
        -- SplicingDiffData
        -- TSSCount
        -- TSSReplicateData
    - CDS
        -- CDS
        -- CDSData
        -- CDSExpDiffData
        -- CDSCount
        -- CDSReplicateData
        
'''
# Allow models to define fields to be displayed in the list view
options.DEFAULT_NAMES += ('list_display',)

# Common fields for different track views
TRACK_BASE_FIELDS = ('locus', 'length', 'coverage',)
TRACK_DATA_FIELDS = ('sample', 'fpkm', 'conf_hi', 'conf_lo', 'status',)
TRACK_COUNT_FIELDS = ('sample', 'count', 'variance', 'uncertainty', 'dispersion', 'status',)
TRACK_REPLICATE_FIELDS = ('sample', 'replicate', 'raw_frags', 'internal_scaled_frags', 'external_scaled_frags', 'fpkm', 'status',)
TRACK_EXPDIFF_FIELDS = ('value_1', 'value_2', 'log2_fold_change', 'status', 'p_value', 'q_value', 'significant',)
TRACK_DIFF_FIELDS = ('value_1', 'value_2', 'js_dist', 'status', 'p_value', 'q_value', 'significant',)

#
# Abstract classes
#

class TrackBaseManager(models.Manager):
    def for_exp(self, exp):
        return super(TrackBaseManager, self).get_query_set().filter(experiment=exp)


class TrackBase(models.Model):
    # We need Char primary key that is computed from track_base_id 
    # and experiment in order to work around the lack of composite
    # primary key support.
    track_pk = models.CharField(max_length=75, unique=True, db_index=True)
    
    experiment = models.ForeignKey('Experiment')
    class_code = models.CharField(max_length=45, db_index=True, null=True)
    nearest_ref_id = models.CharField(max_length=45, db_index=True)
    gene_short_name = models.CharField(max_length=250, db_index=True)
    locus = models.CharField(max_length=45)
    length = models.IntegerField(null=True)
    coverage = models.FloatField(null=True)
    
    objects = TrackBaseManager()
    
    class Meta:
        abstract = True
        
class DiffData(models.Model):
    '''
    Descendants from this model can not be arranged as ManyToMany with
    `through` table because they have two fks to the Sample table.
    '''
    sample_1 = models.ForeignKey('Sample', to_field='sample_pk', related_name='+')
    sample_2 = models.ForeignKey('Sample', to_field='sample_pk', related_name='+')
    status = models.CharField(max_length=45, db_index=True)
    value_1 = models.FloatField()
    value_2 = models.FloatField()
    # log2_fold_change = models.FloatField() - This one will be defined
    # in descendants
    test_stat = models.FloatField()
    p_value = models.FloatField()
    q_value = models.FloatField()
    significant = models.CharField(max_length=45, db_index=True)
    
    class Meta:
        abstract = True
        
class Data(models.Model):
    sample = models.ForeignKey('Sample', to_field='sample_pk')
    fpkm = models.FloatField()
    conf_hi = models.FloatField()
    conf_lo = models.FloatField()
    status = models.CharField(max_length=45)
    
    class Meta:
        abstract = True

class CountData(models.Model):
    sample = models.ForeignKey('Sample', to_field='sample_pk')
    count = models.FloatField()
    variance = models.FloatField()
    uncertainty = models.FloatField()
    dispersion = models.FloatField()
    status = models.CharField(max_length=45)
    
    class Meta:
        abstract = True

class ReplicateData(models.Model):
    sample = models.ForeignKey('Sample', to_field='sample_pk')
    rep_name = models.ForeignKey('Replicate', to_field='rep_pk')
    replicate = models.IntegerField()
    raw_frags = models.FloatField()
    internal_scaled_frags = models.FloatField()
    external_scaled_frags = models.FloatField()
    fpkm = models.FloatField()
    effective_length = models.FloatField(null=True)
    status = models.CharField(max_length=45)
    
    class Meta:
        abstract = True
#
# Experiment level data
#

class Experiment(models.Model):
    '''
    Experiment, e.g. cuffdiff run comparing two (or more) samples.
    '''
    title = models.CharField('Experiment title', max_length=100)
    species = models.CharField('Species', max_length=100)
    library = models.CharField('Library type, e.g. RNA-seq', max_length=100)
    run_date = models.DateField('Date of the run')
    analysis_date = models.DateField('Date of analysis')
    description = models.TextField('Description of the experiment', null=True)
    
    class Meta:
        ordering = ('analysis_date', 'run_date',)
        
    def __unicode__(self):
        return 'Exp %d (%s)' % (self.id, self.title[:25])


class Sample(models.Model):
    '''
    Populated from the first file processed, i.e. genes.fpkm_tracking
    Then checked for mismatch during every subsequent file processing.
    
    sample_name contains description of the the sample such as
    `control`, `treatment`, `wt`, `mut`, etc.
    
    Has many-to-many relationship through corresponding intermediary
    table with Gene, TSS, CDS, and Isoform level tables.
    '''
    experiment = models.ForeignKey(Experiment)
    sample_index = models.IntegerField('Sample index within one experiment')
    sample_name = models.CharField(max_length=45)
    # A substitute for composite pk
    sample_pk = models.CharField(max_length=75, unique=True, db_index=True)
    gene_data = models.ManyToManyField('Gene', through='GeneData',
        related_name='data')
    gene_count = models.ManyToManyField('Gene', through='GeneCount',
        related_name='count')
    gene_replicate = models.ManyToManyField('Gene', 
        through='GeneReplicateData', related_name='replicate')
    tss_data = models.ManyToManyField('TSS', through='TSSData',
        related_name='data')
    tss_count = models.ManyToManyField('TSS', through='TSSCount',
        related_name='count')
    tss_replicate = models.ManyToManyField('TSS', 
        through='TSSReplicateData', related_name='replicate')
    cds_data = models.ManyToManyField('CDS', through='CDSData',
        related_name='data')
    cds_count = models.ManyToManyField('CDS', through='CDSCount',
        related_name='count')
    cds_replicate = models.ManyToManyField('CDS', 
        through='CDSReplicateData', related_name='replicate')
    isoform_data = models.ManyToManyField('Isoform', through='IsoformData',
        related_name='data')
    isoform_count = models.ManyToManyField('Isoform', 
        through='IsoformCount', related_name='count')
    isoform_replicate = models.ManyToManyField('Isoform', 
        through='IsoformReplicateData', related_name='replicate')
    
    class Meta:
        unique_together = ('sample_name', 'experiment',)
        ordering = ('sample_name', 'sample_index',)
        
    def __unicode__(self):
        return 'Sample %d (%s)' % (self.sample_index, self.sample_name)
        
    def save(self, *args, **kwargs):
        self.sample_index = self.experiment.sample_set.count() + 1
        super(Sample, self).save(*args, **kwargs)


class PhenoData(models.Model):
    '''
    Apparently stores additional info about samples
    '''
    sample_name = models.ForeignKey(Sample)
    parameter = models.CharField(max_length=45)


class Replicate(models.Model):
    '''
    Populated from reads_group.info file
        `file_name` refers to the ./<ID>_thout/accepted_hits.bam file
        `sample` is the condition such as control or treatment
        `rep_name` gets constructed from sample and replicate
        `replicate` is the (0-based) replicate number
    '''
    file_name = models.CharField(max_length=200) # Originally file, integer
    sample = models.ForeignKey(Sample, to_field='sample_pk')
    replicate = models.IntegerField()
    # A substitute for composite pk
    rep_pk = models.CharField(max_length=45, unique=True, db_index=True)
    rep_name = models.CharField(max_length=45)
    total_mass = models.FloatField()
    norm_mass = models.FloatField()
    internal_scale = models.FloatField()
    external_scale = models.FloatField()
    


class RunInfo(models.Model):
    '''
    Populated from run.info file
    Currently contains:
        - the command line used to execute cuff_diff
        - version
        - SVN revision
        - boost library version
    '''
    experiment = models.ForeignKey(Experiment)
    key = models.CharField(max_length=45)
    value = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Run info'
        
    def __unicode__(self):
        return '%s:\t%s' % (self.key, self.value)
    
#
# Gene level data
#

class GeneTrackDataManager(models.Manager):
    def for_exp(self, exp):
        return super(GeneTrackDataManager, self).get_query_set().filter(gene__experiment=exp)

class GeneTrackMixin(models.Model):
    '''
    A mixin providing custom manager for gene track data
    '''
    objects = GeneTrackDataManager()
    
    class Meta:
        abstract = True

class Gene(TrackBase):
    '''
    Populated from genes.fpkm_tracking columns 1-3, 5, 7-9:
        - tracking_id
        - class_code
        - nearest_ref_id
        - gene_short_name
        - locus
        - length
        - coverage
    '''
    gene_id = models.CharField(max_length=45, db_index=True)
    
    class Meta:
        ordering = ['gene_id',]
        list_display = ('gene_short_name', 'gene_id',) + TRACK_BASE_FIELDS
    
    def __unicode__(self):
        return '%s (%s)' % (self.gene_id, self.gene_short_name)
        
class GeneData(Data, GeneTrackMixin):
    '''
    Populated from the molten form of genes.fpkm_tracking
    
    sample_name is extracted from column names and is converted to the
    ForeignKey to Sample table. <cond>_conf_hi becomes conf_hi etc.
    
    Likewise, gene_id is converted to the ForeignKey to Gene table.
    '''
    gene = models.ForeignKey(Gene, to_field='track_pk')
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_DATA_FIELDS
        verbose_name_plural = 'gene data'
    
    def __unicode__(self):
        return 'Gene data for %s' % self.gene
        
class GeneExpDiffData(DiffData, GeneTrackMixin):
    '''
    Populated from gene_exp.diff columns 1, 5-14
    sample_name(s) are extracted from column names and converted to the
    ForeignKey to Sample table.
    '''
    gene = models.ForeignKey(Gene, to_field='track_pk')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_EXPDIFF_FIELDS
        verbose_name = 'gene differential expression data'
        verbose_name_plural = 'gene differential expression data'
    
    def __unicode__(self):
        return 'Differential expression data for %s' % self.gene
        
# I am not sure this is needed actually or how it's joined with Feature
# table
class GeneFeature(models.Model):
    gene = models.OneToOneField(Gene, to_field='track_pk')
    
class GeneCount(CountData, GeneTrackMixin):
    '''
    Populated from the molten form of genes.count_tracking
    
    sample_name is extracted from the column names and converted to the
    ForeignKey to Sample table.
    A ForeignKey to Gene table is added.
    '''
    gene = models.ForeignKey(Gene, to_field='track_pk')
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_COUNT_FIELDS
        verbose_name_plural = 'gene count data'
    
    def __unicode__(self):
        return 'Gene count data for %s' % self.gene
        
class GeneReplicateData(ReplicateData, GeneTrackMixin):
    '''
    Populated from genes.read_group_tracking
    If the number of replicates is greater than 1
    creates a unique replicate name by combining condition and number
    then inserts all the data
    '''
    gene = models.ForeignKey(Gene, to_field='track_pk')
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_REPLICATE_FIELDS
        verbose_name_plural = 'gene replicate data'
    
    def __unicode__(self):
        return 'Gene replicate data for %s' % self.gene
        
#
# Annotation level 
#

# Is it a many-to-many to Gene table?
# TODO: rewrite it as a tag-like structure
class Feature(models.Model):
    '''
    Populated by parsing .gtf file.
    Following field conversions are made:
        transcript_id --> isoform_id
        tss_id --> TSS_group_id
        p_id --> CDS_id
    The rest of the fields are kept as is (?)
    '''
    gene = models.ForeignKey(Gene, to_field='track_pk')
    isoform = models.ForeignKey("Isoform", to_field='track_pk')
    seqnames = models.CharField(max_length=45, db_index=True)
    source = models.CharField(max_length=45)
    type_id = models.IntegerField(db_index=True)
    start = models.IntegerField(db_index=True)
    end = models.IntegerField(db_index=True)
    score = models.FloatField()
    strand = models.CharField(max_length=45, db_index=True)
    frame = models.CharField(max_length=45)
    
class Attribute(models.Model):
    feature = models.ForeignKey(Feature)
    attribute = models.CharField(max_length=45)
    value = models.CharField(max_length=45)
    
#
# TSS Group level data
#

class TSSTrackDataManager(models.Manager):
    def for_exp(self, exp):
        return super(TSSTrackDataManager, self).get_query_set().filter(tss_group__experiment=exp)

class TSSTrackMixin(models.Model):
    '''
    A mixin providing custom manager for TSS track data
    '''
    objects = TSSTrackDataManager()
    
    class Meta:
        abstract = True


class TSS(TrackBase):
    tss_group_id = models.CharField(max_length=45, db_index=True)
    gene = models.ForeignKey(Gene, to_field='track_pk')
    
    class Meta:
        ordering = ['tss_group_id',]
        list_display = ('tss_group_id', 'gene',) + TRACK_BASE_FIELDS
        verbose_name = 'TSS group'
        verbose_name_plural = 'TSS groups'
    
    def __unicode__(self):
        return '{tss} ({gene})'.format(tss=self.tss_group_id, gene=self.gene.gene_short_name)


class TSSFeature(models.Model):
    tss_group = models.OneToOneField(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['tss_group',]
        
class TSSData(Data, TSSTrackMixin):
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['tss_group',]
        list_display = ('tss_group',) + TRACK_DATA_FIELDS
        verbose_name_plural = 'TSS data'
    
class TSSExpDiffData(DiffData, TSSTrackMixin):
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['tss_group',]
        list_display = ('tss_group',) + TRACK_EXPDIFF_FIELDS
        verbose_name_plural = 'TSS differential expression data'
        
class TSSCount(CountData, TSSTrackMixin):
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['tss_group',]
        list_display = ('tss_group',) + TRACK_COUNT_FIELDS
        verbose_name_plural = 'TSS count data'
        
class TSSReplicateData(ReplicateData, TSSTrackMixin):
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['tss_group',]
        list_display = ('tss_group',) + TRACK_REPLICATE_FIELDS
        verbose_name_plural = 'TSS replicate data'
#
# CDS Group level data
#

class CDSTrackDataManager(models.Manager):
    def for_exp(self, exp):
        return super(CDSTrackDataManager, self).get_query_set().filter(cds__experiment=exp)

class CDSTrackMixin(models.Model):
    '''
    A mixin providing custom manager for CDS track data
    '''
    objects = CDSTrackDataManager()
    
    class Meta:
        abstract = True


class CDS(TrackBase):
    cds_id = models.CharField(max_length=45, db_index=True)
    gene = models.ForeignKey(Gene, to_field='track_pk')
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['cds_id',]
        list_display = ('cds_id',) + TRACK_BASE_FIELDS
        verbose_name = 'CDS'
        verbose_name_plural = 'CDS'
    
    def __unicode__(self):
        return '{cds} ({gene})'.format(cds=self.cds_id, gene=self.gene.gene_short_name)
        
        
class CDSData(Data, CDSTrackMixin):
    cds = models.ForeignKey(CDS, to_field='track_pk')
    
    class Meta:
        ordering = ['cds',]
        list_display = ('cds',) + TRACK_DATA_FIELDS
        verbose_name_plural = 'CDS data'
    
class CDSCount(CountData, CDSTrackMixin):
    cds = models.ForeignKey(CDS, to_field='track_pk')
    
    class Meta:
        ordering = ['cds',]
        list_display = ('cds',) + TRACK_COUNT_FIELDS
        verbose_name_plural = 'CDS count data'
    
class CDSFeature(models.Model):
    cds = models.ForeignKey(CDS, to_field='track_pk')
    
    class Meta:
        ordering = ['cds',]
    
class CDSExpDiffData(DiffData, CDSTrackMixin):
    cds = models.ForeignKey(CDS, to_field='track_pk')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['cds',]
        list_display = ('cds',) + TRACK_EXPDIFF_FIELDS
        verbose_name_plural = 'CDS differential expression data'
    
class CDSReplicateData(ReplicateData,CDSTrackMixin):
    cds = models.ForeignKey(CDS, to_field='track_pk')
    
    class Meta:
        ordering = ['cds',]
        list_display = ('cds',) + TRACK_REPLICATE_FIELDS
        verbose_name_plural = 'CDS replicate data'
    
#
# Isoform level data
#

class IsoformTrackDataManager(models.Manager):
    def for_exp(self, exp):
        return super(IsoformTrackDataManager, self).get_query_set().filter(isoform__experiment=exp)

class IsoformTrackMixin(models.Model):
    '''
    A mixin providing custom manager for Isoform track data
    '''
    objects = IsoformTrackDataManager()
    
    class Meta:
        abstract = True


class Isoform(TrackBase):
    isoform_id = models.CharField(max_length=45, db_index=True)
    gene = models.ForeignKey(Gene, to_field='track_pk')
    # Currently there is no p_id in isoforms.fpkm_tracking file
    cds = models.ForeignKey(CDS, to_field='track_pk', null=True, blank=True)
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    
    class Meta:
        ordering = ['isoform_id',]
        list_display = ('gene', 'tss_group', 'isoform_id',) + TRACK_BASE_FIELDS
    
    def __unicode__(self):
        return '{isoform} ({gene})'.format(isoform=self.isoform_id, gene=self.gene.gene_short_name)


class IsoformData(Data, IsoformTrackMixin):
    isoform = models.ForeignKey(Isoform, to_field='track_pk')
    
    class Meta:
        ordering = ['isoform',]
        list_display = ('isoform',) + TRACK_DATA_FIELDS
        verbose_name_plural = 'Isoform data'
    
class IsoformCount(CountData, IsoformTrackMixin):
    isoform = models.ForeignKey(Isoform, to_field='track_pk')
    
    class Meta:
        ordering = ['isoform',]
        list_display = ('isoform',) + TRACK_COUNT_FIELDS
        verbose_name_plural = 'Isoform count data'
    
class IsoformFeature(models.Model):
    isoform = models.OneToOneField(Isoform,to_field='track_pk')
    
    class Meta:
        ordering = ['isoform',]
    
class IsoformExpDiffData(DiffData, IsoformTrackMixin):
    isoform = models.ForeignKey(Isoform, to_field='track_pk')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['isoform',]
        list_display = ('isoform',) + TRACK_EXPDIFF_FIELDS
        verbose_name_plural = 'Isoform differential expression data'
    
class IsoformReplicateData(ReplicateData, IsoformTrackMixin):
    isoform = models.ForeignKey(Isoform, to_field='track_pk')
    
    class Meta:
        ordering = ['isoform',]
        list_display = ('isoform',) + TRACK_REPLICATE_FIELDS
        verbose_name_plural = 'Isoform replicate data'
    
#
# Dist level data
#

class CDSDiffData(DiffData, GeneTrackMixin):
    gene = models.ForeignKey(Gene, to_field='track_pk')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_DIFF_FIELDS
        verbose_name_plural = 'CDS differential usage data'
    
class PromoterDiffData(DiffData, GeneTrackMixin):
    gene = models.ForeignKey(Gene, to_field='track_pk')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        list_display = ('gene',) + TRACK_DIFF_FIELDS
        verbose_name_plural = 'Promoter differential usage data'
    
class SplicingDiffData(DiffData, TSSTrackMixin):
    tss_group = models.ForeignKey(TSS, to_field='track_pk')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['tss_group',]
        list_display = ('tss_group',) + TRACK_DIFF_FIELDS
        verbose_name_plural = 'Splicing data'
