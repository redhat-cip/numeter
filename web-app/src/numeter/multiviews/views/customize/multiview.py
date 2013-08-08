from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Multiview
from multiviews.forms import Multiview_Form
from json import dumps as jdumps


@login_required()
def index(request):
    q = request.GET.get('q','')
    multiviews = Multiview.objects.user_web_filter(q, request.user)
    multiviews = make_page(multiviews, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/multiview/index.html', {
        'Multiviews': multiviews,
        'q':q,
    })


@login_required()
def list(request):
    q = request.GET.get('q','')
    multiviews = Multiview.objects.user_web_filter(q, request.user)
    multiviews = make_page(multiviews, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/multiview/list.html', {
        'Multiviews': multiviews,
        'q':q,
    })


@login_required()
def add(request):
    return render(request, 'customize/view/multiview.html', {
       'Multiview_Form': Multiview_Form(),
    })


@login_required()
def edit(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(id=multiview_id))
    F = Multiview_Form(instance=M)
    return render(request, 'customize/multiview/multiview.html', {
        'Multiview_Form': F,
    })


@login_required()
def fast_add(request):
    M = Multiview.objects.create(name=request.POST['multiview_name'])
    M.views.add(V)
    r = V.get_data_dygraph(res=request.POST.get('res','Daily'))
    return HttpResponse(jdumps(r), content_type="application/json")
