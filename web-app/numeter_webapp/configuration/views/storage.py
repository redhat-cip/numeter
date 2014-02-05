from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Storage, Host
from configuration.forms.storage import Storage_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def get(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    F = Storage_Form(instance=S)
    return render(request, 'storages/storage.html', {
        'Storage_Form': F,
    })


@login_required()
@superuser_only()
def add(request):
    return render(request, 'storages/storage.html', {
        'Storage_Form': Storage_Form(),
    })


@login_required()
@superuser_only()
def bad_hosts(request):
    if request.method == 'GET':
        hosts = Storage.objects.get_bad_referenced_hostids()
        return render(request, 'storages/bad-host-list.html', {
            'Hosts': Host.objects.filter(hostid__in=hosts),
        })
    else:
        Storage.objects.repair_hosts()
        messages.success(request, _("Hosts fixing finished."))
        return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def create_hosts(request, storage_id):
    Storage.objects.get(id=storage_id).create_hosts()
    messages.success(request, _("Hosts creation finished."))
    return render(request, 'base/messages.html', {})
