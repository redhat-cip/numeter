from django.shortcuts import render
from core.utils.decorators import login_required
from multiviews.models import Multiview


@login_required()
def multiviews_index(request):
    multiviews = Multiview.objects.user_filter(request.user)

    return render(request, 'multiviews-index.html', {
        'multiviews': multiviews,
        'title': 'Numeter - Multiviews',
    })
