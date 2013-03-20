from django import template
from django.db.models.loading import get_model
from django.utils.http import urlencode


register = template.Library()

@register.simple_tag(takes_context=True)
def render_track_header(context, fields):
    th_tmpl = '<th>{field}</th>'
    return ''.join([th_tmpl.format(field=f.replace('_',' ')) for f in fields])


@register.simple_tag(takes_context=True)
def render_track_obj(context, obj):
    fields = obj._meta.list_display
    td_tmpl = '<td>{field}</td>'
    row = ''.join([td_tmpl.format(field=getattr(obj,f)) for f in fields])
    return '<tr>%s</tr>' % row


@register.simple_tag
def stat(track, exp):
    track_model = get_model('cuff', track)
    return track_model._default_manager.for_exp(exp).count()


@register.inclusion_tag('cuff/includes/th_sort.html', takes_context=True)
def sort_by(context, field, text):
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
        'link': text,
        }


@register.inclusion_tag('cuff/includes/crumbs.html', takes_context=True)
def crumbs(context):
    request = context['request']
    bits = request.path.strip('/').split('/')
    return { 'crumbs': bits,}
    
