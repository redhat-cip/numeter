from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Plugin, Data_Source
from multiviews.forms import Plugin_Form
from core.models import Host
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page


@login_required()
@superuser_only()
def index(request):
    """Get plugins and hosts list."""
    Plugins = Plugin.objects.all()
    Plugins_count = Plugins.count()
    Plugins = make_page(Plugins, 1, 20)
    return render(request, 'conf/plugins/index.html', {
        'Plugins': Plugins,
        'Plugins_count': Plugins_count,
        'Sources_count': Data_Source.objects.count(),
        'Hosts': Host.objects.all(),
    })


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Plugins = Plugin.objects.web_filter(q)
    Plugins = make_page(Plugins, int(request.GET.get('page',1)), 20)
    return render(request, 'conf/plugins/plugin-list.html', {
        'Plugins': Plugins,
        'Hosts': Host.objects.all(),
        'q':q,
    })


@login_required()
@superuser_only()
def create_from_host(request):
    if request.method == 'POST':
        host = Host.objects.get(id=request.POST['host_id'])
        plugins = Plugin.objects.create_from_host(host, request.POST.getlist('plugins[]'))
        messages.success(request, _("Plugin(s) created with success."))
        return render(request, 'base/messages.html', {})
    else:
        host = Host.objects.get(id=request.GET['host_id'])
        plugins = Plugin.objects.get_unsaved_plugins(host)
        return render(request, 'conf/plugins/create-plugins.html', {
            'plugins':plugins,
            'host':host,
        })



@login_required()
@superuser_only()
def get(request, plugin_id):
    P = get_object_or_404(Plugin.objects.filter(pk=plugin_id))
    F = Plugin_Form(instance=P)
    return render(request, 'conf/plugins/plugin.html', {
        'Plugin_Form': F,
    })


@login_required()
@superuser_only()
def update(request, plugin_id):
    P = get_object_or_404(Plugin.objects.filter(pk=plugin_id))
    F = Plugin_Form(data=request.POST, instance=P)
    if F.is_valid():
        F.save()
        messages.success(request, _("Plugin updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, plugin_id):
    P = get_object_or_404(Plugin.objects.filter(pk=plugin_id))
    P.delete()
    messages.success(request, _("Plugin deleted with success."))
    return render(request, 'base/messages.html', {})

# TODO
# @login_required()
# @superuser_only()
# def list_sources(request, plugin_id):
#     sources = Plugin.objects.get(id=plugin_id).get_data_sources()
#     messages.success(request, _("Sources creation finished."))
#     return render(request, 'base/messages.html', {})

@login_required()
@superuser_only()
def create_sources(request, plugin_id):
    P = get_object_or_404(Plugin.objects.filter(pk=plugin_id))
    if request.method == 'POST':
        P.create_data_sources(request.POST.getlist('sources[]'))
        messages.success(request, _("Sources creation finished."))
        return render(request, 'base/messages.html', {})
    else:
        return render(request, 'conf/plugins/create-sources.html', {
            'plugin': P,
            'sources': P.get_unsaved_sources()
        })
