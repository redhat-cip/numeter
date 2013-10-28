from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Skeleton
from configuration.forms.skeleton import Skeleton_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Skeletons = Skeleton.objects.web_filter(q)
    Skeletons = make_page(Skeletons, int(request.GET.get('page',1)), 20)
    return render(request, 'views/skeleton-list.html', {
        'Skeletons': Skeletons,
        'q':q,
    })


@login_required()
def add(request):
    if request.method == 'POST':
        F = Skeleton_Form(data=request.POST)
        data = {}
        if F.is_valid():
            S = F.save()
            messages.success(request, _("Skeleton added with success."))
            data.update({
              'response': 'ok',
              'callback-url': S.get_absolute_url(),
              'id': S.pk,
            })
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'forms/skeleton.html', {
            'Skeleton_Form': Skeleton_Form(),
        })


@login_required()
@superuser_only()
def get(request, skeleton_id):
    S = get_object_or_404(Skeleton.objects.filter(pk=skeleton_id))
    F = Skeleton_Form(instance=S)
    return render(request, 'forms/skeleton.html', {
        'Skeleton_Form': F,
    })


@login_required()
@superuser_only()
def update(request, skeleton_id):
    S = get_object_or_404(Skeleton.objects.filter(pk=skeleton_id))
    F = Skeleton_Form(data=request.POST, instance=S)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("Skeleton updated with success."))
        data.update({
          'response': 'ok',
          'callback-url': S.get_absolute_url(),
          'id': S.id,
        })
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, skeleton_id):
    S = get_object_or_404(Skeleton.objects.filter(pk=skeleton_id))
    S.delete()
    messages.success(request, _("Skeleton deleted with success."))
    return render(request, 'base/messages.html', {})


# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several skeletons in one request."""
    skeletons = Skeleton.objects.filter(pk__in=request.POST.getlist('ids[]'))
    skeletons.delete()
    messages.success(request, _("Skeleton(s) deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
