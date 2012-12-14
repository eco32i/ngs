from django import forms

from cuff.models import Sample

# Form field names are directly used to filter queryset in the view
# Ugly but works for now.

#
# Abstract base forms
#
class BaseDataFilterForm(forms.Form):
    sample__pk = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input-medium',}))
    fpkm__gte = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'fpkm min...'}))


class BaseCountFilterForm(forms.Form):
    sample__pk = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input-medium',}))
    count__gte = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'count min...'}))


class BaseReplicateDataFilterForm(forms.Form):
    sample__pk = forms.ModelChoiceField(
        queryset=Sample.objects.all(),
        widget=forms.Select(attrs={
            'class': 'input-medium',}))
    replicate = forms.IntegerField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-mini',
            'placeholder': 'replicate number...'}))
    fpkm__gte = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'fpkm min...'}))


class BaseExpDiffDataFilterForm(forms.Form):
    p_value__lte = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'p value max...'}))
    q_value__lte = forms.DecimalField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'q value max...'}))
    significant = forms.CharField(required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-mini',
            'placeholder': 'sig ...',}))


class GeneTrackMixin(forms.Form):
    gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))


class TSSTrackMixin(forms.Form):
    tss_group__gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    tss_group__gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))


class IsoformTrackMixin(forms.Form):
    isoform__gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    isoform__gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))
            
            
class CDSTrackMixin(forms.Form):
    cds__gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    cds__gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))


#
# Gene track forms
#
class GeneFilterForm(forms.Form):
    gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))


class GeneDataFilterForm(BaseDataFilterForm, GeneTrackMixin):
    '''
    GeneData filters form
    '''


class GeneCountFilterForm(BaseCountFilterForm, GeneTrackMixin):
    '''
    GeneCount filters form
    '''


class GeneReplicateDataFilterForm(BaseReplicateDataFilterForm, GeneTrackMixin):
    '''
    GeneReplicateData filters form
    '''


class GeneExpDiffDataFilterForm(BaseExpDiffDataFilterForm, GeneTrackMixin):
    '''
    GeneExpDiffData filters form
    '''


#
# TSS track forms
#
class TSSFilterForm(forms.Form):
    gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))
    tss_group_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'tss group id (TSS)...'}))


class TSSDataFilterForm(BaseDataFilterForm, TSSTrackMixin):
    '''
    TSSData filters form
    '''


class TSSCountFilterForm(BaseCountFilterForm, TSSTrackMixin):
    '''
    TSSCount filters form
    '''

class TSSReplicateDataFilterForm(BaseReplicateDataFilterForm, TSSTrackMixin):
    '''
    TSSReplicateData filters form
    '''


class TSSExpDiffDataFilterForm(BaseExpDiffDataFilterForm, TSSTrackMixin):
    '''
    TSSExpDiffData filters form
    '''


#
# Isoform track forms
#
class IsoformFilterForm(forms.Form):
    gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))
    isoform_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'isoform id (TCONS)...'}))


class IsoformDataFilterForm(BaseDataFilterForm, IsoformTrackMixin):
    '''
    IsoformData filters form
    '''


class IsoformCountFilterForm(BaseCountFilterForm, IsoformTrackMixin):
    '''
    IsoformCount filters form
    '''

class IsoformReplicateDataFilterForm(BaseReplicateDataFilterForm, IsoformTrackMixin):
    '''
    IsoformReplicateData filters form
    '''


class IsoformExpDiffDataFilterForm(BaseExpDiffDataFilterForm, IsoformTrackMixin):
    '''
    IsoformExpDiffData filters form
    '''


#
# CDS track forms
#
class CDSFilterForm(forms.Form):
    gene__gene_short_name = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene short name...',}))
    gene__gene_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'gene id (XLOC)...'}))
    cds_id = forms.CharField(max_length=45, required=False,
        widget=forms.TextInput(attrs={
            'class': 'input-medium',
            'placeholder': 'CDS id (Pxxx)...'}))


class CDSDataFilterForm(BaseDataFilterForm, CDSTrackMixin):
    '''
    CDSData filters form
    '''


class CDSCountFilterForm(BaseCountFilterForm, CDSTrackMixin):
    '''
    CDSCount filters form
    '''

class CDSReplicateDataFilterForm(BaseReplicateDataFilterForm, CDSTrackMixin):
    '''
    CDSReplicateData filters form
    '''


class CDSExpDiffDataFilterForm(BaseExpDiffDataFilterForm, CDSTrackMixin):
    '''
    CDSExpDiffData filters form
    '''


#
# Distribution level forms
#
