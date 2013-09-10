from django import template
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.utils.http import urlencode


register = template.Library()

@register.simple_tag(takes_context=True)
def render_track_obj(context, obj):
    fields = obj._meta.list_display
    td_tmpl = '<td>{field}</td>'
    row = ''.join([td_tmpl.format(field=getattr(obj,f)) for f in fields])
    return '<tr>%s</tr>' % row


@register.inclusion_tag('cuff/includes/th_sort.html', takes_context=True)
def render_header_field(context, field):
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


@register.inclusion_tag('cuff/includes/crumbs.html', takes_context=True)
def crumbs(context):
    request = context['request']
    bits = request.path.strip('/').split('/')
    return { 'crumbs': bits,}
    
