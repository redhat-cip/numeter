from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Host
from configuration.forms.host import Host_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def get(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    F = Host_Form(instance=H)
    return render(request, 'storages/host.html', {
        'Host_Form': F,
    })


@login_required()
@superuser_only()
def plugins(request, host_id):
    H = get_object_or_404(Host.objects.filter(pk=host_id))
    plugins = H.get_plugins()
    return render(request, 'storages/plugin-list.html', {
      'plugins': plugins
    })
