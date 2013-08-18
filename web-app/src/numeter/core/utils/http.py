from django.http import HttpResponse
from django.template import RequestContext, loader
from json import dumps as jdumps

def render_HTML_JSON(request, json, template, context):
    template = loader.get_template(template)
    context = RequestContext(request, context)
    json['html'] = template.render(context)

    return HttpResponse(jdumps(json), content_type="application/json")
