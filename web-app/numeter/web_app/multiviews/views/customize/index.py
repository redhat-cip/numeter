from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required
from core.utils import make_page
from core.models import Host, Data_Source
from multiviews.models import Multiview, View
from multiviews.forms.view import Small_View_Form as View_Form
from multiviews.forms.multiview import Small_Multiview_Form as Multiview_Form
from multiviews.forms.event import Small_Event_Form as Event_Form


@login_required()
def index(request):
    sources = Data_Source.objects.user_filter(request.user)
    sources = make_page(sources, 1, 10)

    views = View.objects.user_filter(request.user)
    views = make_page(views, 1, 10)

    multiviews = Multiview.objects.user_filter(request.user)
    multiviews = make_page(multiviews, 1, 10)

    events = Multiview.objects.user_filter(request.user)
    events = make_page(events, 1, 10)

    return render(request, 'customize/index.html', {
        'Hosts': Host.objects.user_filter(request.user),
        'Sources': sources,
        'Views': views,
        'View_Form': View_Form(user=request.user),
        'Multiviews': multiviews,
        'Multiview_Form': Multiview_Form(user=request.user),
        'Events': events,
        'Event_Form': Event_Form(user=request.user),
    })
