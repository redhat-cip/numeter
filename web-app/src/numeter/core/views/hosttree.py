from django.shortcuts import render, redirect, get_object_or_404
from core.models import Host
from core.utils.decorators import login_required


@login_required()
def group(request, group_id=None):
    return render(request, 'hosttree/group.html', {
        'hosts': Host.objects.filter(group=group_id),
    }) 


@login_required()
def host(request, host_id=None):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/host.html', {
        'category': H.get_categories(),
    }) 


@login_required()
def category(request, host_id, category):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/category.html', {
        'category': H.get_plugins_by_category(),
    }) 

# NOW USELESS
@login_required()
def get_plugins_by_host(request, host_id=None):
    H = get_object_or_404(Host.objects.filter(id=host_id))
    return render(request, 'hosttree/plugins.html', {
        'plugins': H.get_plugins(),
    }) 
