from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern):
    import re
    print request.path
    try:
        if re.search(pattern, request.path):
            return 'active'
        return ''
    except:
        return 'active'
