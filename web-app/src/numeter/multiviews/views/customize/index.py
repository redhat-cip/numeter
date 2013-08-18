from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Multiview, View, Data_Source
from configuration.forms.view import View_Form
from configuration.forms.multiview import Multiview_Form


@login_required()
def index(request):
    sources = Data_Source.objects.user_filter(request.user)
    sources = make_page(sources, 1, 10)

    views = View.objects.user_filter(request.user)
    views = make_page(views, 1, 10)

    multiviews = Multiview.objects.user_filter(request.user)
    multiviews = make_page(multiviews, 1, 10)

    return render(request, 'customize/index.html', {
        'Sources': sources,
        'Views': views,
        'View_Form': View_Form(),
        'Multiviews': multiviews,
        'Multiview_Form': Multiview_Form(),
    })
