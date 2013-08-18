from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Host
from core.forms import Host_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def host_list(request):
    q = request.GET.get('q','')
    Hosts = Host.objects.web_filter(q)
    Hosts = make_page(Hosts, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/storages/host-list.html', {
        'Hosts': Hosts,
        'q':q,
    })


@login_required()
@superuser_only()
def host_get(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    F = Host_Form(instance=H)
    return render(request, 'configuration/storages/host.html', {
        'Host_Form': F,
    })


@login_required()
@superuser_only()
def host_update(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    F = Host_Form(data=request.POST, instance=H)
    if F.is_valid():
        F.save()
        messages.success(request, _("Host updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def host_delete(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    H.delete()
    messages.success(request, _("Host deleted with success."))
    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def host_plugins(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    plugins = H.get_plugins()
    return render(request, 'configuration/storages/plugin-list.html', {
      'plugins': plugins
    })


# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several hosts in one request."""
    hosts = Host.objects.filter(pk__in=request.POST.getlist('ids[]'))
    hosts.delete()
    messages.success(request, _("Hosts deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
