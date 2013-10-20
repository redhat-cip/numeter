from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import View, Multiview
from multiviews.forms.view import Small_View_Form as View_Form

from json import dumps as jdumps


# Maybe useless
@login_required()
def index(request):
    q = request.GET.get('q','')
    views = View.objects.user_web_filter(q, request.user)
    views = make_page(views, int(request.GET.get('page',1)), 30)
    return render(request, 'customize/view/index.html', {
        'Views': views,
        'q':q,
    })


@login_required()
def add(request):
    """Only for get empty View_Form."""
    return render(request, 'forms/view.html', {
       'View_Form': View_Form(user=request.user),
    })


@login_required()
def list(request):
    q = request.GET.get('q','')
    views = View.objects.user_web_filter(q, request.user)
    views = make_page(views, int(request.GET.get('page',1)), 30)
    return render(request, 'customize/view/list.html', {
        'Views': views,
        'q':q,
    })


@login_required()
def edit(request, view_id):
    """Only in GET, POST is conf/add."""
    V = get_object_or_404(View.objects.filter(id=view_id))
    F = View_Form(instance=V, user=request.user)
    return render(request, 'forms/view.html', {
        'View_Form': F,
    })


@login_required()
def fast_add(request):
    M = get_object_or_404(Multiview.objects.filter(pk=request.POST['multiview_id']))
    V = View.objects.create(name=request.POST['view_name'])
    M.views.add(V)
    r = V.get_extended_data(res=request.POST.get('res','Daily'))
    return HttpResponse(jdumps(r), content_type="application/json")


@login_required()
def fast_add_source(request, view_id):
    sources_ids = request.POST.getlist('source_ids[]')
    V = get_object_or_404(View.objects.filter(pk=view_id))
    for s in sources_ids:
        try: 
            V.sources.add(s)
        except:
            pass
    messages.success(request, _("Source added with success."))
    return render(request, 'base/messages.html', {})


@login_required()
def fast_remove_source(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    sources_nums = request.POST.getlist('source_nums[]')
    sources = [ V.sources.all()[int(i)] for i in sources_nums ]
    [ V.sources.remove(s) for s in sources ]
    messages.success(request, _("Source removed with success."))
    return render(request, 'base/messages.html', {})
