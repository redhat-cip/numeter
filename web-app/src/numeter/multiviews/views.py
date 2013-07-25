from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from core.utils.decorators import login_required
from multiviews.models import Multiview, View
from json import dumps as jdumps


@login_required()
def multiviews_index(request):
    multiviews = Multiview.objects.get_user_multiview(request.user)

    return render(request, 'multiviews-index.html', {
        'multiviews': multiviews,
        'title': 'Numeter - Multiviews',
    })

@login_required()
def get_data(request, view_id):
    M = get_object_or_404(View.objects.filter(id=view_id))
    r = M.get_data_dygraph()
    return HttpResponse(jdumps(r), content_type="application/json")
