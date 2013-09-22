from django import template
from django.core.urlresolvers import resolve

register = template.Library()

@register.filter(name='active_hyperlink')
def active_hyperlink(request, url_name):
    if url_name == resolve(request.path).url_name:
        return 'active'
    else:
        return ''
