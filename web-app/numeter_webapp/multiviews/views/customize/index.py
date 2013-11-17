from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Multiview, View, Event
from configuration.forms.view import Extended_View_Form as View_Form


@login_required()
def index(request):
    views = View.objects.user_filter(request.user)
    views = make_page(views, 1, 30)
    return render(request, 'customize/index.html', {
        'Views': views,
        'View_Form': View_Form(user=request.user),
    })
