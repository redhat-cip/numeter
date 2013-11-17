from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from core.utils.decorators import login_required
from core.models import Data_Source
from multiviews.models import Multiview, View
from json import dumps as jdumps


@login_required()
def view(request, view_id):
    V = get_object_or_404(View.objects.filter(id=view_id))
    r = V.get_extended_data(res=request.GET.get('res','Daily'))
    return HttpResponse(jdumps(r), content_type="application/json")


@login_required()
def source(request, source_id):
    S = get_object_or_404(Data_Source.objects.filter(id=source_id))
    r = S.get_extended_data(res=request.GET.get('res','Daily'))
    return HttpResponse(jdumps(r), content_type="application/json")

