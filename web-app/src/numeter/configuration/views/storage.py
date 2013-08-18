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
def index(request):
    """Get storages and hosts list."""
    Storages = Storage.objects.all()
    Storages_count = Storages.count()
    Storages = make_page(Storages, 1, 20)
    return render(request, 'storages/index.html', {
        'Storages': Storages,
        'Storages_count': Storages_count,
        'Hosts_count': Host.objects.count(),
        #'Bad_hosts_count': len(Storage.objects.get_bad_referenced_hostids())
    })


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Storages = Storage.objects.web_filter(q)
    Storages = make_page(Storages, int(request.GET.get('page',1)), 20)
    return render(request, 'storages/storage-list.html', {
        'Storages': Storages,
        'q':q,
    })


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
    if request.method == 'POST':
        F = Storage_Form(request.POST)
        data = {}
        if F.is_valid():
            S = F.save()
            messages.success(request, _("Storage added with success."))
            data['response'] = 'ok'
            data['callback-url'] = S.get_absolute_url()
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'storages/storage.html', {
            'Storage_Form': Storage_Form(),
        })


@login_required()
@superuser_only()
def update(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    F = Storage_Form(data=request.POST, instance=S)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("Storage updated with success."))
        data['response'] = 'ok'
        data['callback-url'] = S.get_absolute_url()
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    S.delete()
    messages.success(request, _("Storage deleted with success."))
    return render(request, 'base/messages.html', {})


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
