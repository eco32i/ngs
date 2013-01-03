from django import template
from django.template.context import Context
from django.utils.http import urlencode


register = template.Library()

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
    
