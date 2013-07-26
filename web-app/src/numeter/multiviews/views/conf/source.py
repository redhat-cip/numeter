from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Data_Source
from multiviews.forms import Data_Source_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page


@login_required()
@superuser_only()
def list(request):
    Sources = Data_Source.objects.all()
    q = request.GET.get('q','')
    if q:
        Sources = Sources.filter(name__icontains=request.GET.get('q',''))
    Sources = make_page(Sources, int(request.GET.get('page',1)), 20)
    return render(request, 'conf/plugins/source-list.html', {
        'Sources': Sources,
        'q':q,
    })


@login_required()
@superuser_only()
def get(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(pk=source_id))
    F = Data_Source_Form(instance=S)
    return render(request, 'conf/plugins/source.html', {
        'Source_Form': F,
    })


@login_required()
@superuser_only()
def update(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(pk=source_id))
    F = Data_Source_Form(data=request.POST, instance=S)
    if F.is_valid():
        F.save()
        messages.success(request, _("Source updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(pk=source_id))
    S.delete()
    messages.success(request, _("Source deleted with success."))
    return render(request, 'base/messages.html', {})


# TODO
@login_required()
@superuser_only()
def add_to_view(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(pk=source_id))
    return render(request, 'conf/plugins/plugin-list.html', {
      'plugins': plugins
    })
