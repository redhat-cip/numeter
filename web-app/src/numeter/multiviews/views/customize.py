from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Multiview, View, Data_Source
from multiviews.forms import Data_Source_Form, View_Form
from json import dumps as jdumps


@login_required()
def index(request):
    sources = Data_Source.objects.user_filter(request.user)
    sources = make_page(sources, 1, 10)

    views = View.objects.user_filter(request.user)
    views = make_page(views, 1, 10)

    multiviews = Multiview.objects.get_user_multiview(request.user)

    return render(request, 'customize/index.html', {
        'Sources': sources,
        'Views': views,
    })


@login_required()
def source_index(request):
    q = request.GET.get('q','')
    Sources = Data_Source.objects.user_web_filter(q, request.user)
    Sources = make_page(Sources, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/source/index.html', {
        'Sources': Sources,
        'q':q,
    })


@login_required()
def source_list(request):
    q = request.GET.get('q','')
    Sources = Data_Source.objects.user_web_filter(q, request.user)
    Sources = make_page(Sources, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/source/add.html', {
        'Sources': Sources,
        'q':q,
    })


@login_required()
def source_edit(request, source_id):
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

    F = Data_Source_Form(instance=S)
    return render(request, 'customize/source/edit.html', {
        'Source_Form': F,
    })


@login_required()
def add_source_to_view(request, view_id):
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
def remove_source_from_view(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    sources_nums = request.POST.getlist('source_nums[]')
    sources = [ V.sources.all()[int(i)] for i in sources_nums ]
    [ V.sources.remove(s) for s in sources ]
    messages.success(request, _("Source removed with success."))
    return render(request, 'base/messages.html', {})


@login_required()
def view_add(request):
    M = get_object_or_404(Multiview.objects.filter(pk=request.POST['multiview_id']))
    V = View.objects.create(name=request.POST['view_name'])
    M.views.add(V)
    r = V.get_data_dygraph(res=request.POST.get('res','Daily'))
    return HttpResponse(jdumps(r), content_type="application/json")


@login_required()
def multiview_add(request):
    M = Multiview.objects.create(pk=request.POST['multiview_name'])
    r = ''
    return HttpResponse(jdumps(r), content_type="application/json")


@login_required()
def view_index(request):
    q = request.GET.get('q','')
    Views = Data_View.objects.user_web_filter(q, request.user)
    Views = make_page(Views, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/view/index.html', {
        'Views': Views,
        'q':q,
    })


@login_required()
def view_list(request):
    q = request.GET.get('q','')
    views = View.objects.user_web_filter(q, request.user)
    views = make_page(views, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/view/list.html', {
        'Views': views,
        'q':q,
    })


@login_required()
def view_edit(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    if request.method == 'POST':
        F = View_Form(instance=V, data=request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("View updated with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})

    F = View_Form(instance=V)
    return render(request, 'customize/view/edit.html', {
        'View_Form': F,
    })
