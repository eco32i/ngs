from django.db import models

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

#
# Abstract classes
#

class TrackBase(models.Model):
    class_code = models.CharField(max_length=45, db_index=True, null=True)
    nearest_ref_id = models.CharField(max_length=45, db_index=True)
    gene_short_name = models.CharField(max_length=250, db_index=True)
    locus = models.CharField(max_length=45)
    length = models.IntegerField(null=True)
    coverage = models.FloatField(null=True)
    
    class Meta:
        abstract = True
        
class DiffData(models.Model):
    '''
    Descendants from this model can not be arranged as ManyToMany with
    `through` table because they have two fks to the Sample table.
    '''
    sample_1 = models.ForeignKey('Sample', to_field='sample_name', related_name='+')
    sample_2 = models.ForeignKey('Sample', to_field='sample_name', related_name='+')
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
    sample = models.ForeignKey('Sample', to_field='sample_name')
    fpkm = models.FloatField()
    conf_hi = models.FloatField()
    conf_lo = models.FloatField()
    status = models.CharField(max_length=45)
    
    class Meta:
        abstract = True

class CountData(models.Model):
    sample = models.ForeignKey('Sample', to_field='sample_name')
    count = models.FloatField()
    variance = models.FloatField()
    uncertainty = models.FloatField()
    dispersion = models.FloatField()
    status = models.CharField(max_length=45)
    
    class Meta:
        abstract = True

class ReplicateData(models.Model):
    sample = models.ForeignKey('Sample', to_field='sample_name')
    rep_name = models.ForeignKey('Replicate', to_field='rep_name')
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

class Sample(models.Model):
    '''
    Populated from the first file processed, i.e. genes.fpkm_tracking
    Then checked for mismatch during every subsequent file processing.
    
    sample_name contains description of the the sample such as
    `control`, `treatment`, `wt`, `mut`, etc.
    
    Has many-to-many relationship through corresponding intermediary
    table with Gene, TSS, CDS, and Isoform level tables.
    '''
    sample_index = models.IntegerField()
    sample_name = models.CharField(max_length=45, unique=True)
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
        ordering = ('sample_name', 'sample_index', )
        
    def __unicode__(self):
        return 'Sample %d (%s)' % (self.sample_index, self.sample_name)
        
    def save(self, *args, **kwargs):
        if len(self._default_manager.all()) == 0:
            self.sample_index = 1
        elif not self.id:
            self.sample_index = self._default_manager.all().order_by('-pk')[0].pk + 1
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
    sample = models.ForeignKey(Sample, to_field='sample_name')
    replicate = models.IntegerField()
    rep_name = models.CharField(max_length=45, unique=True)
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
    key = models.CharField(max_length=45)
    value = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Run info'
        
    def __unicode__(self):
        return '%s:\t%s' % (self.key, self.value)
    
#
# Gene level data
#

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
    gene_id = models.CharField(max_length=45, unique=True, db_index=True)
    
    class Meta:
        ordering = ['gene_id',]
    
    def __unicode__(self):
        return '%s (%s)' % (self.gene_id, self.gene_short_name)
        
class GeneData(Data):
    '''
    Populated from the molten form of genes.fpkm_tracking
    
    sample_name is extracted from column names and is converted to the
    ForeignKey to Sample table. <cond>_conf_hi becomes conf_hi etc.
    
    Likewise, gene_id is converted to the ForeignKey to Gene table.
    '''
    gene = models.ForeignKey(Gene, to_field='gene_id')
    
    class Meta:
        ordering = ['gene',]
        verbose_name_plural = 'gene data'
    
    def __unicode__(self):
        return 'Gene data for %s' % self.gene
        
class GeneExpDiffData(DiffData):
    '''
    Populated from gene_exp.diff columns 1, 5-14
    sample_name(s) are extracted from column names and converted to the
    ForeignKey to Sample table.
    '''
    gene = models.ForeignKey(Gene, to_field='gene_id')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        verbose_name = 'gene differential expression data'
        verbose_name_plural = 'gene differential expression data'
    
    def __unicode__(self):
        return 'Differential expression data for %s' % self.gene
        
# I am not sure this is needed actually or how it's joined with Feature
# table
class GeneFeature(models.Model):
    gene = models.OneToOneField(Gene, to_field='gene_id')
    
class GeneCount(CountData):
    '''
    Populated from the molten form of genes.count_tracking
    
    sample_name is extracted from the column names and converted to the
    ForeignKey to Sample table.
    A ForeignKey to Gene table is added.
    '''
    gene = models.ForeignKey(Gene, to_field='gene_id')
    
    class Meta:
        ordering = ['gene',]
        verbose_name_plural = 'gene count data'
    
    def __unicode__(self):
        return 'Gene count data for %s' % self.gene
        
class GeneReplicateData(ReplicateData):
    '''
    Populated from genes.read_group_tracking
    If the number of replicates is greater than 1
    creates a unique replicate name by combining condition and number
    then inserts all the data
    '''
    gene = models.ForeignKey(Gene, to_field='gene_id')
    
    class Meta:
        ordering = ['gene',]
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
    gene = models.ForeignKey(Gene, to_field='gene_id')
    isoform = models.ForeignKey("Isoform", to_field='isoform_id')
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

class TSS(TrackBase):
    tss_group_id = models.CharField(max_length=45, unique=True, db_index=True)
    gene = models.ForeignKey(Gene, to_field='gene_id')
    
    class Meta:
        ordering = ['tss_group_id',]
        verbose_name = 'TSS group'
        verbose_name_plural = 'TSS groups'
    
class TSSFeature(models.Model):
    tss_group = models.OneToOneField(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['tss_group',]
        
class TSSData(Data):
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['tss_group',]
        verbose_name_plural = 'TSS data'
    
class TSSExpDiffData(DiffData):
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['tss_group',]
        verbose_name_plural = 'TSS differential expression data'
        
class TSSCount(CountData):
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['tss_group',]
        verbose_name_plural = 'TSS count data'
        
class TSSReplicateData(ReplicateData):
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['tss_group',]
        verbose_name_plural = 'TSS replicate data'
#
# CDS Group level data
#

class CDS(TrackBase):
    cds_id = models.CharField(max_length=45, unique=True, db_index=True)
    gene = models.ForeignKey(Gene, to_field='gene_id')
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['cds_id',]
        verbose_name = 'CDS'
        verbose_name_plural = 'CDS'
    
class CDSData(Data):
    cds = models.ForeignKey(CDS, to_field='cds_id')
    
    class Meta:
        ordering = ['cds',]
        verbose_name_plural = 'CDS data'
    
class CDSCount(CountData):
    cds = models.ForeignKey(CDS, to_field='cds_id')
    
    class Meta:
        ordering = ['cds',]
        verbose_name_plural = 'CDS count data'
    
class CDSFeature(models.Model):
    cds = models.ForeignKey(CDS, to_field='cds_id')
    
    class Meta:
        ordering = ['cds',]
    
class CDSExpDiffData(DiffData):
    cds = models.ForeignKey(CDS, to_field='cds_id')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['cds',]
        verbose_name_plural = 'CDS differential expression data'
    
class CDSReplicateData(ReplicateData):
    cds = models.ForeignKey(CDS, to_field='cds_id')
    
    class Meta:
        ordering = ['cds',]
        verbose_name_plural = 'CDS replicate data'
    
#
# Isoform level data
#

class Isoform(TrackBase):
    isoform_id = models.CharField(max_length=45, unique=True, db_index=True)
    gene = models.ForeignKey(Gene, to_field='gene_id')
    # Currently there is no p_id in isoforms.fpkm_tracking file
    cds = models.ForeignKey(CDS, to_field='cds_id', null=True, blank=True)
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    
    class Meta:
        ordering = ['isoform_id',]
    
class IsoformData(Data):
    isoform = models.ForeignKey(Isoform, to_field='isoform_id')
    
    class Meta:
        ordering = ['isoform',]
        verbose_name_plural = 'Isoform data'
    
class IsoformCount(CountData):
    isoform = models.ForeignKey(Isoform, to_field='isoform_id')
    
    class Meta:
        ordering = ['isoform',]
        verbose_name_plural = 'Isoform count data'
    
class IsoformFeature(models.Model):
    isoform = models.OneToOneField(Isoform,to_field='isoform_id')
    
    class Meta:
        ordering = ['isoform',]
    
class IsoformExpDiffData(DiffData):
    isoform = models.ForeignKey(Isoform, to_field='isoform_id')
    log2_fold_change = models.FloatField()
    
    class Meta:
        ordering = ['isoform',]
        verbose_name_plural = 'Isoform differential expression data'
    
class IsoformReplicateData(ReplicateData):
    isoform = models.ForeignKey(Isoform, to_field='isoform_id')
    
    class Meta:
        ordering = ['isoform',]
        verbose_name_plural = 'Isoform replicate data'
    
#
# Dist level data
#

class CDSDiffData(DiffData):
    gene = models.ForeignKey(Gene, to_field='gene_id')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        verbose_name_plural = 'CDS differential usage data'
    
class PromoterDiffData(DiffData):
    gene = models.ForeignKey(Gene, to_field='gene_id')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['gene',]
        verbose_name_plural = 'Promoter differential usage data'
    
class SplicingDiffData(DiffData):
    tss_group = models.ForeignKey(TSS, to_field='tss_group_id')
    js_dist = models.FloatField()
    
    class Meta:
        ordering = ['tss_group',]
        verbose_name_plural = 'Splicing data'
