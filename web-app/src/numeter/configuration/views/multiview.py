from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Multiview
from configuration.forms.multiview import Multiview_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Multiviews = Multiview.objects.web_filter(q)
    Multiviews = make_page(Multiviews, int(request.GET.get('page',1)), 20)
    return render(request, 'views/multiview-list.html', {
        'Multiviews': Multiviews,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    if request.method == 'POST':
        F = Multiview_Form(request.POST)
        data = {}
        if F.is_valid():
            M = F.save()
            messages.success(request, _("Multiview added with success."))
            data['response'] = 'ok'
            data['callback-url'] = M.get_absolute_url()
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'views/multiview.html', {
            'Multiview_Form': Multiview_Form(),
        })


@login_required()
@superuser_only()
def get(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    F = Multiview_Form(instance=M)
    return render(request, 'views/multiview.html', {
        'Multiview_Form': F,
    })


@login_required()
@superuser_only()
def update(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    F = Multiview_Form(data=request.POST, instance=M)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("Multiview updated with success."))
        data['response'] = 'ok'
        data['callback-url'] = M.get_absolute_url()
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})

@login_required()
@superuser_only()
def delete(request, multiview_id):
    M = get_object_or_404(Multiview.objects.filter(pk=multiview_id))
    M.delete()
    messages.success(request, _("Multiview deleted with success."))
    return render(request, 'base/messages.html', {})


# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several multiviews in one request."""
    multiviews = Multiview.objects.filter(pk__in=request.POST.getlist('ids[]'))
    multiviews.delete()
    messages.success(request, _("Multiview(s) deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
