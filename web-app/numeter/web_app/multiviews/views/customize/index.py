from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required
from core.utils import make_page
from core.models import Host, Data_Source
from multiviews.models import Multiview, View, Event
from multiviews.forms.view import Small_View_Form as View_Form
from multiviews.forms.multiview import Small_Multiview_Form as Multiview_Form
from multiviews.forms.event import Small_Event_Form as Event_Form


@login_required()
def index(request):
    views = View.objects.user_filter(request.user)
    views = make_page(views, 1, 30)
    return render(request, 'customize/index.html', {
        'Views': views,
        'View_Form': View_Form(user=request.user),
    })
