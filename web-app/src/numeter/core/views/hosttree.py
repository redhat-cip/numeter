from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Host
from core.utils.decorators import login_required
from json import dumps as jdumps


@login_required()
def group(request, group_id=None):
    return render(request, 'hosttree/group.html', {
        'group': Host.objects.filter(group__id=group_id)
    }) 


@login_required()
def host(request, host_id=None):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/host.html', {
        'host': H.get_categories(),
    }) 


@login_required()
def category(request, host_id):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/category.html', {
        'category': H.get_plugins_by_category(request.GET['category']),
    }) 


@login_required()
def get_data(request, host_id, plugin):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    data = {'plugin':'Processes%20priority', 'ds':'nice', 'res':'Daily'}
    r = [ g for g in H.get_data_dygraph(**data) ]
    return HttpResponse(jdumps(r), content_type="application/json")

# NOW USELESS
@login_required()
def get_plugins_by_host(request, host_id=None):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/plugins.html', {
        'plugins': H.get_plugins(),
    }) 
