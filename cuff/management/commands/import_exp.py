import os, csv
from optparse import make_option

from django.db.models.loading import get_model
from django.core.management.base import BaseCommand, CommandError

from cuff.models import (Experiment, Sample, Replicate, RunInfo,
    Gene, TSS, ExpStat, PromoterDiffData, SplicingDiffData, CDSDiffData)

# The filenames from cuffdiff output
RUNINFO_FILE = 'run.info'
REPLICATES_FILE = 'read_groups.info'
GENE_FPKM_FILE = 'genes.fpkm_tracking'
GENEEXP_DIFF_FILE = 'gene_exp.diff'
PROMOTER_FILE = 'promoters.diff'
GENE_COUNT_FILE = 'genes.count_tracking'
GENE_REPLICATE_FILE = 'genes.read_group_tracking'
ISOFORM_FPKM_FILE = 'isoforms.fpkm_tracking'
ISOFORMEXP_DIFF_FILE = 'isoform_exp.diff'
ISOFORM_COUNT_FILE = 'isoforms.count_tracking'
ISOFORM_REPLICATE_FILE = 'isoforms.read_group_tracking'
TSS_FPKM_FILE = 'tss_groups.fpkm_tracking'
TSSEXP_DIFF_FILE = 'tss_group_exp.diff'
SPLICING_FILE = 'splicing.diff'
TSS_COUNT_FILE = 'tss_groups.count_tracking'
TSS_REPLICATE_FILE = 'tss_groups.read_group_tracking'
CDS_FPKM_FILE = 'cds.fpkm_tracking'
CDSEXP_DIFF_FILE = 'cds_exp.diff'
CDS_DIFF_FILE = 'cds.diff'
CDS_COUNT_FILE = 'cds.count_tracking'
CDS_REPLICATE_FILE = 'cds.read_group_tracking'

# This whole mess should be refactored using pandas or such...

class Command(BaseCommand):
    '''
    Imports the files produced by cuff_diff into the database.
    Files are assumed to be .tsv with the first line as header.
    
    Loading is going in the following order:
        - RunInfo
        - RepTable (also populates Sample)
        - Genes
        - Isoforms
        - TSS
        - CDS
    '''
    option_list = BaseCommand.option_list + (
        make_option('--exclude', default='', dest='exclude',
            help='Track to exclude'),
        make_option('--exp-title', default='', dest='title',
            help='Experiment title. Inferred from the directory name if not given.'),
        make_option('--exp-species', default='C.elegans', dest='species',
            help='Species'),
        make_option('--exp-lib-type', default='RNA-Seq', dest='lib',
            help='Library type (e.g. mRNA-seq'),
        make_option('--gtf', default=None, dest='gtf',
            help='.gtf file with annotations'),
        make_option('--genome-build', default=None, dest='gbuild',
            help='genome build information'),
        )
    args = '<cuffdiff out directory>'
    
    def _get_reader(self, file, header=None):
        return csv.DictReader(file, delimiter='\t', fieldnames=header)
    
    def _get_track_fields(self, model):
        '''
        returns all fields except for `id` for a given model
        '''
        raw_fields = model._meta.get_all_field_names()
        return filter(lambda x: x != 'id', raw_fields)
        
    def _get_track(self, model_track, data_track):
        '''
        model_track is Gene, TSS, CDS, Isoform etc
        data_track is *data, *diff, etc.
        '''
        track_model = get_model('cuff', model_track)
        if model_track == 'tss':
            track_field = 'tss_group'
        else:
            track_field = model_track
        if data_track == 'diffdata':
            # these are 3 special cases where we have distribution
            # level diff data
            if model_track == 'gene':
                data_model = PromoterDiffData
            elif model_track == 'tss':
                data_model = SplicingDiffData
            elif model_track == 'cds':
                data_model = CDSDiffData
                track_field = 'gene'
        else:
            data_model = get_model('cuff', 
                '{track}{data}'.format(track=model_track, data=data_track)
                )
        return track_model, data_model, track_field
    
    def _track_melt(self, model, track_id_field, data):

        def is_foreign_key(model, field):
            field, m, direct, m2m = model._meta.get_field_by_name(field)
            return field.rel and direct

        fields = model._meta.get_all_field_names()
        kwargs = {'experiment': self.exp,}
        for k,v in data.items():
            if k.endswith('_id'):
                # Handle foreign keys and primary keys here
                key_base, dummy = k.split('_id')
                if key_base == 'tss':
                    key_base = 'tss_group'
                if k == 'tracking_id':
                    # k is tracking id -- compute track_pk and set track_id field
                    track_key = '{track}_id'.format(track=track_id_field)
                    kwargs.update({
                        track_key: v,
                        # This is an ugly way of getting composite pk.
                        'track_pk': '{base_id}-exp-{exp_id}'.format(base_id=v,exp_id=self.exp.pk),
                        })
                elif key_base in fields and is_foreign_key(model, key_base):
                    # k is a foreign key to either gene or tss_group
                    kwargs.update({
                        '{0}_id'.format(key_base): '{base_id}-exp-{exp_id}'.format(
                            base_id=v,exp_id=self.exp.pk),
                        })
            # '-' denotes NA value
            elif k in fields and v != '-':
                # k is just a regular field
                kwargs.update({k: v,})
        return model(**kwargs)
    
    def _data_melt(self, model, track_id_field, sample_names, data):
        '''
        Kinda sorta analogous to dataframe.melt function in R.
        '''
        fields = self._get_track_fields(model)
        track_key = '{track}_id'.format(track=track_id_field)
        melts = [{'sample_id': name, track_key: '{base_id}-exp-{exp_id}'.format(base_id=data['tracking_id'], exp_id=self.exp.pk), } 
            for name in sample_names]
        for k,v in data.items():
            sample_name = k.split('_')[0]
            for m in melts:
                if sample_name == m['sample_id']:
                    kwargs = m
                    break
            for field in fields:
                if k.lower().endswith(field) and v != '-':
                    kwargs.update({field: v,})
        for m in melts:
            m['sample_id'] += '-exp-{exp_pk}'.format(exp_pk=self.exp.pk)
        return [model(**kwargs) for kwargs in melts]
        
    def _process_fpkm(self, track, file):
        # Get track model, data model, track_id field and related lookup
        track_model, data_model, track_id = self._get_track(track, 'data')
        track_records = []
        data_records = []
        sample_names = Sample.objects.filter(experiment=self.exp).values_list('sample_name', flat=True)
        with open(file) as fpkm_file:
            reader = self._get_reader(fpkm_file)
            self.stdout.write('\t...\treshaping data...')
            for rec in reader:
                track_records.append(self._track_melt(track_model, track_id, rec))
                data_records.extend(self._data_melt(data_model, track_id, 
                    sample_names, rec))
        self.stdout.write('\t...\twriting tables...')
        track_count = len(track_model._default_manager.bulk_create(track_records))
        data_count = len(data_model._default_manager.bulk_create(data_records))
        self.stdout.write('\t...\t {tcount} {track} and {dcount} {track}data records ...'.format( 
                tcount=track_count,
                track=track,
                dcount=data_count))
        return track_count, data_count
    
    def _process_diff(self, track, file, diff='expdiffdata'):
        '''
        This can probably be used for all track bases.
        Just needs to be passed the track or model.
        '''
        track_model, diff_model, track_id_field = self._get_track(track, diff)
        track_key = '{track}_id'.format(track=track_id_field)
        fields = diff_model._meta.get_all_field_names()
        imported = []
        with open(file) as diff_file:
            reader = self._get_reader(diff_file)
            self.stdout.write('\t...\tparsing data...')
            for rec in reader:
                kwargs = {track_key: '{base_id}-exp-{exp_id}'.format(base_id=rec['test_id'], exp_id=self.exp.pk),}
                for k,v in rec.items():
                    if k in fields:
                        if k.startswith('sample'):
                            # FIXME: Sample pk!
                            sample_key = '{sample}_id'.format(sample=k)
                            kwargs.update({sample_key: '{name}-exp-{exp_pk}'.format(name=v, exp_pk=self.exp.pk),})
                        elif k != track_id_field:
                            kwargs.update({k: v,})
                    elif k.startswith('sqrt'):
                        kwargs.update({'js_dist': v,})
                    elif k.startswith('log2'):
                        kwargs.update({'log2_fold_change': v,})
                imported.append(diff_model(**kwargs))
        self.stdout.write('\t...\twriting tables...')
        diff_count = len(diff_model._default_manager.bulk_create(imported))
        self.stdout.write('\t...\t {count} records processed'.format(count=diff_count))
        return diff_count
    
    def _process_count(self, track, count):
        # FIXME: Broken. This one misses uncertainty_var!
        track_model, count_model, track_id_field = self._get_track(track, 'count')
        fields = self._get_track_fields(count_model)
        track_key = '{track}_id'.format(track=track_id_field)
        sample_names = Sample.objects.filter(experiment=self.exp).values_list('sample_name', flat=True)
        imported = []
        with open(count) as count_file:
            reader = self._get_reader(count_file)
            # Handle stupid tss naming convention
            for rec in reader:
                # Set up list of kwargs for every sample
                tracking_id = rec.pop('tracking_id')
                melts = [{'sample_id': name, track_key: '{base_id}-exp-{exp_id}'.format(base_id=tracking_id, exp_id=self.exp.pk),}
                        for name in sample_names]
                for k,v in rec.items():
                    bits = k.split('_')
                    sample_name = bits.pop(0)
                    for m in melts:
                        if sample_name == m['sample_id']:
                            kwargs = m
                            break
                    for f in bits:
                        # This will break if field name contains 
                        # underscore
                        if f in fields and not f in kwargs:
                            kwargs.update({f: v,})
                for m in melts:
                    m['sample_id'] += '-exp-{exp_pk}'.format(exp_pk=self.exp.pk)
                imported.extend([count_model(**melt) for melt in melts])
        cnt_count = len(count_model._default_manager.bulk_create(imported))
        self.stdout.write('\t...\t {count} records processed'.format(count=cnt_count))
        return cnt_count
    
    def _process_replicate(self, track, replicate):
        track_model, rep_model, track_id_field = self._get_track(track, 'replicatedata')
        fields = self._get_track_fields(rep_model)
        track_key = '{track}_id'.format(track=track_id_field)
        imported = []
        with open(replicate) as rep_file:
            reader = self._get_reader(rep_file)
            for rec in reader:
                kwargs = {track_key: '{base_id}-exp-{exp_id}'.format(base_id=rec['tracking_id'], exp_id=self.exp.pk),}
                for k,v in rec.items():
                    f = k.lower()
                    if f in fields and v != '-':
                        kwargs.update({f: v,})
                    elif f == 'condition':
                        # sample = v
                        kwargs.update({'sample_id': '{sample}-exp-{exp_pk}'.format(
                            sample=v,
                            exp_pk=self.exp.pk),}
                            )
                kwargs.update({'rep_name_id': '{sample}_{rep}-exp-{exp_pk}'.format(
                    sample=rec['condition'],
                    rep=rec['replicate'],
                    exp_pk=self.exp.pk),}
                    )
                imported.append(rep_model(**kwargs))
        rep_count = len(rep_model._default_manager.bulk_create(imported))
        self.stdout.write('\t...\t {count} records processed'.format(count=rep_count))
        return rep_count
    
    def set_options(self, dir, **options):
        '''
        Set instance variables based on options dict
        '''
        from datetime import datetime as dt
        gtf_file = options['gtf']
        if gtf_file and os.path.exists(gtf_file):
            self.gtf = gtf_file
        else:
            self.gtf = None
        self.genome_build = options['gbuild']
        self.exclude = options['exclude'].split()
        info = os.stat(dir)
        created = dt.fromtimestamp(info.st_mtime)
        self.exp = Experiment.objects.create(
            title=options['title'] or os.path.basename(dir).replace('_', ' '),
            species=options['species'],
            library=options['lib'],
            analysis_date=created,
            run_date=created,
            )
        
    
    def import_runinfo(self, file):
        '''
        Imports runinfo data as key:value pairs from run.info file
        Currently imports the following:
            - cmd_line: command line command used to invoke cuffdiff
            - version:  cuffdiff version number
            - SVN_revision:  cuffdiff SVN revision
            - boost_version:    version of boost libraries
        '''
        # fields = RunInfo._meta.get_all_field_names()
        imported = []
        with open(file) as runinfo_file:
            reader = self._get_reader(runinfo_file)
            for rec in reader:
                imported.append(RunInfo(
                    experiment=self.exp,
                    key=rec['param'], 
                    value=rec['value']
                ))
        if self.genome_build:
            imported.append(RunInfo(
                experiment=self.exp,
                key='genome',
                value=self.genome_build
                ))
        return RunInfo.objects.bulk_create(imported)
        
    def import_reptable(self, file):
        '''
        Imports replicates data (read_groups.info file)
        Populates Sample table.
        '''
        imported = []
        fields = Replicate._meta.get_all_field_names()
        with open(file) as rep_file:
            reader = self._get_reader(rep_file)
            for rec in reader:
                sample, created = Sample.objects.get_or_create(
                    experiment=self.exp,
                    sample_name=rec['condition'],
                    sample_pk='{sample}-exp-{exp}'.format(
                        sample=rec['condition'],
                        exp=self.exp.pk)
                    )
                kwargs = {
                    'sample': sample,
                    'file_name': rec['file'],
                    'replicate': int(rec['replicate_num']),
                    'rep_pk': '%s_%s-exp-%s' % (rec['condition'], rec['replicate_num'], self.exp.pk),
                    'rep_name': '%s_%s' % (rec['condition'], rec['replicate_num'])
                    }
                for k,v in rec.items():
                    f = k.lower()
                    if f in fields:
                        kwargs.update({f: v,})
                imported.append(Replicate(**kwargs))
        return Replicate.objects.bulk_create(imported)
    
    def import_track(self, track, fpkm, diff, **kwargs):
        '''
        Imports data track
            - Track
            - TrackData
            - TrackExpDiffData
            - TrackCount
            - TrackReplicateData
            - optional tables such as promoters, splicing, cdsdiff, etc
        '''
        if os.path.exists(fpkm):
            self.stdout.write('\t... processing .fpkm file ...')
            track_count = self._process_fpkm(track, fpkm)[0]
        else:
            raise CommandError('%s .fpkm file is missing!' % track)
        if os.path.exists(diff):
            self.stdout.write('\t... processing .diff file ...')
            self._process_diff(track, diff)
        else:
            raise CommandError('%s .diff file is missing!' % track)
        # Optional
        diff_count = 0
        if 'promoter' in kwargs and track == 'gene':
            promoter = kwargs.get('promoter')
            if os.path.exists(promoter):
                self.stdout.write('\t... processing promoters.diff ...')
                diff_count = self._process_diff('gene', promoter, diff='diffdata')
            else:
                raise CommandError('Promoters .diff file is missing!')
        if 'splicing' in kwargs and track == 'tss':
            splicing = kwargs.get('splicing')
            if os.path.exists(splicing):
                self.stdout.write('\t... processing splicing.diff ...')
                diff_count = self._process_diff('tss', splicing, 'diffdata')
            else:
                raise CommandError('Splicing .diff file is missing!')
        if 'cds_diff' in kwargs and track == 'cds':
            cds_diff = kwargs.get('cds_diff')
            if os.path.exists(cds_diff):
                self.stdout.write('\t... processing CDS .diff ...')
                diff_count = self._process_diff('cds', cds_diff, 'diffdata')
            else:
                raise CommandError('CDS .diff file is missing!')
                
        if 'count' in kwargs:
            count = kwargs.get('count')
            if os.path.exists(count):
                self.stdout.write('\t... processing .count_tracking file ...')
                self._process_count(track, count)
        if 'replicate' in kwargs:
            replicate = kwargs.get('replicate')
            if os.path.exists(replicate):
                self.stdout.write('\t... processing .read_group_tracking file ...')
                self._process_replicate(track, replicate)
        self.stdout.write('Finished processing %s track.' % track)
        return track_count, diff_count
        
    def import_gtf(self, file):
        pass
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Invalid number of arguments.')
        dir = args[0]
        if not os.path.exists(dir):
            raise CommandError('Directory %s does not exist.' % dir)
        self.set_options(dir, **options)
        self.stdout.write('Importing experiment:\t{title}'.format(title=self.exp.title))
        self.stdout.write('\t... Species:\t{species}'.format(species=self.exp.species))
        self.stdout.write('\t... Library:\t{lib}'.format(lib=self.exp.library))
        self.stdout.write('Reading Runinfo file ...')
        self.import_runinfo(os.path.join(dir, RUNINFO_FILE))
        self.stdout.write('Importing replicates and populating Samples table ...')
        self.import_reptable(os.path.join(dir, REPLICATES_FILE))
        if not 'gene' in self.exclude:
            self.stdout.write('Importing genes ...')
            gene_num, promoter_num = self.import_track('gene', os.path.join(dir, GENE_FPKM_FILE),
                os.path.join(dir, GENEEXP_DIFF_FILE),
                promoter=os.path.join(dir, PROMOTER_FILE),
                count=os.path.join(dir, GENE_COUNT_FILE),
                replicate=os.path.join(dir, GENE_REPLICATE_FILE)
                )
        if not 'TSS' in self.exclude:
            self.stdout.write('Importing TSS groups ...')
            tss_num, splicing_num = self.import_track('tss', os.path.join(dir, TSS_FPKM_FILE),
                os.path.join(dir, TSSEXP_DIFF_FILE),
                splicing=os.path.join(dir, SPLICING_FILE),
                count=os.path.join(dir, TSS_COUNT_FILE),
                replicate=os.path.join(dir, TSS_REPLICATE_FILE)
                )
        if not 'isoform' in self.exclude:
            self.stdout.write('Importing isoforms ...')
            isoform_num = self.import_track('isoform', os.path.join(dir, ISOFORM_FPKM_FILE),
                os.path.join(dir, ISOFORMEXP_DIFF_FILE),
                count=os.path.join(dir, ISOFORM_COUNT_FILE),
                replicate=os.path.join(dir, ISOFORM_REPLICATE_FILE)
                )[0] # Because there is no dist level data here
        if not 'CDS' in self.exclude:
            self.stdout.write('Importing CDS ...')
            cds_num, relcds_num = self.import_track('cds', os.path.join(dir, CDS_FPKM_FILE),
                os.path.join(dir, CDSEXP_DIFF_FILE),
                cds_diff=os.path.join(dir, CDS_DIFF_FILE),
                count=os.path.join(dir, CDS_COUNT_FILE),
                replicate=os.path.join(dir, CDS_REPLICATE_FILE)
                )
        # Now dump all the stats into a separate table for an easy
        # access later
        ExpStat.objects.create(
            experiment=self.exp,
            gene_count=gene_num,
            promoter_count=promoter_num,
            tss_count=tss_num,
            splicing_count=splicing_num,
            isoform_count=isoform_num,
            cds_count=cds_num,
            relcds_count=relcds_num
        )
        if self.gtf:
            self.stdout.write('Importing .GTF file ...')
            self.import_gtf(self.gtf)
        self.stdout.write('DONE.')
