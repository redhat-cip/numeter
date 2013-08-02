from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Multiview
from multiviews.forms import Multiview_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Multiviews = Multiview.objects.web_filter(q)
    Multiviews = make_page(Multiviews, int(request.GET.get('page',1)), 20)
    return render(request, 'conf/views/multiview-list.html', {
        'Multiviews': Multiviews,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    if request.method == 'POST':
        F = Multiview_Form(request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("Multiview added with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})
    else:
        return render(request, 'conf/views/multiview.html', {
            'Multiview_Form': Multiview_Form(),
        })


@login_required()
@superuser_only()
def get(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    F = Multiview_Form(instance=M)
    return render(request, 'conf/views/multiview.html', {
        'Multiview_Form': F,
    })


@login_required()
@superuser_only()
def update(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    F = Multiview_Form(data=request.POST, instance=M)
    if F.is_valid():
        F.save()
        messages.success(request, _("Multiview updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    M.delete()
    messages.success(request, _("Multiview deleted with success."))
    return render(request, 'base/messages.html', {})
