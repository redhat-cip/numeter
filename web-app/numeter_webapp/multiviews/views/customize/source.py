from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Host, Data_Source
from multiviews.models import View
from core.utils.decorators import login_required
from core.utils import make_page
from configuration.forms.source import Data_Source_Form
from json import dumps as jdumps


@login_required()
def index(request):
    q = request.GET.get('q','')
    Sources = Data_Source.objects.user_web_filter(q, request.user)
    Sources = make_page(Sources, int(request.GET.get('page',1)), 30)
    return render(request, 'customize/source/index.html', {
        'Hosts': Host.objects.user_filter(request.user),
        'Sources': Sources,
        'q':q,
    })


@login_required()
def list(request):
    q = request.GET.get('q','')
    Sources = Data_Source.objects.user_web_filter(q, request.user)
    Sources = make_page(Sources, int(request.GET.get('page',1)), 30)
    return render(request, 'customize/source/list.html', {
        'Sources': Sources,
        'q':q,
    })


@login_required()
def edit(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(pk=source_id))
    if request.method == 'POST':
        F = Data_Source_Form(instance=S, data=request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("Source updated with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})
    else:
        F = Data_Source_Form(instance=S)
        return render(request, 'customize/source/source.html', {
            'Source_Form': F,
    })

@login_required()
def add(request):
    """Add sources and create plugin if doesn't exist."""
    if request.method == 'GET':
        return render(request, 'customize/source/add.html', {'Hosts':Host.objects.user_filter(request.user)})
    else:
        Data_Source.objects.full_create(request.POST)
        messages.success(request, _("Source(s) added with success."))
        return render(request, 'base/messages.html', {})
