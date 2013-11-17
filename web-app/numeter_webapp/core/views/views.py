from django.shortcuts import render
from django.conf import settings

from core.models import Host
from core.utils.decorators import login_required


@login_required()
def index(request):
    hosts = Host.objects.all()
    if not request.user.is_superuser:
        hosts = hosts.filter(group__in=request.user.groups.all())
    return render(request, 'index.html', {
        'title': 'Numeter',
        'hosts': hosts,
    })


# TODO
# Comments, HTML, URL, JS
def apropos(request):
    with open(settings.BASEDIR+'/../LICENSE') as LICENSE_FILE:
        license = LICENSE_FILE.read()
    return render(request, 'apropos.html', {
        'license': license,
    })
