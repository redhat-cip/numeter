from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Host
from core.forms import Host_Form
from core.utils.decorators import login_required
from core.utils import make_page


@login_required()
def host_list(request):
    Hosts = Host.objects.all()
    q = request.GET.get('q','')
    if q:
        Hosts = Hosts.filter(name__icontains=request.GET.get('q',''))
    Hosts = make_page(Hosts, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/storages/host-list.html', {
        'Hosts': Hosts,
        'q':q,
    })


@login_required()
def host_get(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    F = Host_Form(instance=H)
    return render(request, 'configuration/storages/host.html', {
        'Host_Form': F,
    })


@login_required()
def host_update(request, host_id):
    S = get_object_or_404(Host.objects.filter(pk=host_id))
    F = Host_Form(data=request.POST, instance=S)
    if F.is_valid():
        F.save()
        messages.success(request, _("Host updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
def host_delete(request, host_id):
    S = get_object_or_404(Host.objects.filter(pk=host_id))
    S.delete()
    messages.success(request, _("Host deleted with success."))
    return render(request, 'base/messages.html', {})
