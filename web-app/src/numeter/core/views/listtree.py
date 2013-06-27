from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Host


@login_required()
def get_hosts(request, id):
	return render(request, 'hosttree/hosts.html', {
		'hosts': Host.objects.filter(id=id),
	}) 
