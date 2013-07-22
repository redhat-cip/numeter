from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404

from core.models import Host, Group
from core.utils.decorators import login_required
from core.utils.perms import has_perm

from json import dumps as jdumps


@login_required()
def group(request, group_id=None):
    """Get list of Hosts from a Group."""
    Hs = get_list_or_404(Host, group__id=group_id)
    if not has_perm(request.user, Group, group_id):
        raise Http404
    return render(request, 'hosttree/group.html', {
        'group': Hs,
    }) 


@login_required()
def host(request, host_id=None):
    """Get list of plugin's categories."""
    H = get_object_or_404(Host.objects.filter(id=host_id))
    if not has_perm(request.user, Host, host_id):
        raise Http404
    return render(request, 'hosttree/host.html', {
        'host': H.get_categories(),
    }) 


@login_required()
def category(request, host_id):
    """Get list of plugins of a category."""
    H = get_object_or_404(Host.objects.filter(id=host_id))
    if not has_perm(request.user, Host, host_id):
        raise Http404
    return render(request, 'hosttree/category.html', {
        'category': H.get_plugins_by_category(request.GET['category']),
    }) 


@login_required()
def get_data(request, host_id, plugin):
    """Get JSON data from a plugin."""
    H = get_object_or_404(Host.objects.filter(id=host_id))
    if not has_perm(request.user, Host, host_id):
        raise Http404

    data = {'plugin':plugin, 'ds':'nice', 'res':request.GET.get('res','Daily')}
    r = [ g for g in H.get_data_dygraph(**data) ]
    return HttpResponse(jdumps(r), content_type="application/json")
