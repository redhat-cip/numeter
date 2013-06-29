from django.shortcuts import render
from django.conf import settings

from core.models import Host
from core.utils.decorators import login_required


@login_required()
def index(request):
    return render(request, 'index.html', {
        'title': 'Numeter',
        'hosts': Host.objects.all(),
    })


# TODO
# Comments, HTML, URL, JS
def apropos(request):
    with open(settings.BASEDIR+'/../LICENSE') as LICENSE_FILE:
        license = LICENSE_FILE.read()
    return render(request, 'apropos.html', {
        'license': license,
    })
