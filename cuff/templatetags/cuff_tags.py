from django import template
from django.core.urlresolvers import reverse
from django.utils.http import urlencode


register = template.Library()

@register.simple_tag
def render_track_obj(obj):
    '''
    Renders track `obj` as a table row.
    Fields to render are specified in `obj._meta.list_display` property.
    '''
    fields = obj._meta.list_display
    td_tmpl = '<td>{field}</td>'
    row = ''.join([td_tmpl.format(field=getattr(obj,f)) for f in fields])
    return '<tr>%s</tr>' % row


@register.inclusion_tag('cuff/includes/th_sort.html', takes_context=True)
def render_header_field(context, field):
    '''
    Renders `field` as a clickable sort link in the column header
    of the table for track objects.
    Toggles sorting order (ascending, descending) if `field` is already
    in sort params.
    '''
    request = context['request']
    params = request.GET.copy()
    ordering = params.pop('o', [])
    url_param = field
    css = 'sorting'
    if ordering:
        o = ordering[0]
        if o.startswith('-') and o.endswith(field):
            css = 'sorting-asc'
        elif o == field:
            css = 'sorting-desc'
            url_param = '-%s' % field
    return {
        'css': css,
        'href': '?%s' % urlencode({'o': url_param,}),
        'link': field.replace('_', ' '),
        }

@register.inclusion_tag('cuff/includes/track_menu.html', takes_context=True)
def track_menu(context, track):
    '''
    Renders track menu in the top navigation bar for a given `track`.
    '''
    exp = context['exp']
    track_data = ('data', 'count', 'replicate', 'diff',)
    dist_data = ('promoter', 'splicing', 'relcds',)
    if track == 'dist':
        li_data = [{
            'url': reverse('track_base_view', kwargs={'track': data, 'exp_pk': exp.pk,}),
            'link': data,} for data in dist_data]
    else:
        li_data = list({'url': reverse('track_base_view', kwargs={'track': track, 'exp_pk': exp.pk, }),
                'link': track,})
        for data in track_data:
            li_data.append({
                'url': reverse('track_data_view', kwargs={'track': track, 'exp_pk': exp.pk, 'data': data,}),
                'link': '{track} {data}'.format(track=track, data=data),
                })
    return {'menu_items': li_data,}
    
    
@register.inclusion_tag('cuff/includes/track_summary.html', takes_context=True)
def render_track_summary(context, track):
    '''
    Renders the summary of the given ``track`` along with the links
    to the corresponding list and plot views.
    '''
    exp_stat = context['exp_stat']
    exp_pk = exp_stat.experiment.pk
    att_name = '{0}_count'.format(track)
    track_count = getattr(exp_stat, att_name)
    track_info = track
    if track == 'splicing':
        track_info = 'splice variants'
    elif track == 'relcds':
        track_info = 'rel CDS'
    elif track == 'tss':
        track_info = 'TSS group'
    return {
        'list_url': reverse('track_base_view', kwargs={'track': track, 'exp_pk': exp_pk,}),
        'plot_url': reverse('track_plots_view', kwargs={'track': track, 'exp_pk': exp_pk,}),
        'track': track,
        'track_info': track_info,
        'track_count': track_count,
        }
    
    
@register.inclusion_tag('cuff/includes/crumbs.html', takes_context=True)
def crumbs(context):
    '''
    Renders simple, URL-based breadcrumbs.
    '''
    request = context['request']
    bits = request.path.strip('/').split('/')
    return { 'crumbs': bits,}
    
