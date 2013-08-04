from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Multiview, View, Data_Source
from json import dumps as jdumps


@login_required()
def index(request):
    multiviews = Multiview.objects.get_user_multiview(request.user)
    views = View.objects.user_filter(request.user)
    sources = Data_Source.objects.user_filter(request.user)
    sources = make_page(sources, int(request.GET.get('page',1)), 10)

    return render(request, 'customize/index.html', {
        'Sources': sources,
    })

@login_required()
def source_list(request):
    q = request.GET.get('q','')
    Sources = Data_Source.objects.web_filter(q)
    Sources = make_page(Sources, int(request.GET.get('page',1)), 20)
    return render(request, 'customize/source-list.html', {
        'Sources': Sources,
        'q':q,
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
