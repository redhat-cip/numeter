from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from core.models import Host


@login_required()
def index(request):
	return render(request, 'index.html', {
		'hosts':Host.objects.all(),
	})


# TODO
# Comments, HTML, URL, JS
def apropos(request):
	with open(settings.BASEDIR+'/../../../../LICENSE') as LICENSE_FILE:
		license = LICENSE_FILE.read()
	return render(request, 'apropos.html', {
		'license': license,
	})
