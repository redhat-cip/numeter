from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Host


@login_required()
def get_hosts_by_group(request, id=None):
    return render(request, 'hosttree/hosts.html', {
        'hosts': Host.objects.filter(group=id),
    }) 


@login_required()
def get_plugins_by_host(request, id=None):
    H = Host.objects.get(id=id)
    return render(request, 'hosttree/plugins.html', {
        'plugins': H.get_plugins(),
    }) 
