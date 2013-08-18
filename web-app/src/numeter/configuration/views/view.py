from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import View, Multiview, Data_Source
from configuration.forms.view import View_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def index(request):
    Views = View.objects.all()
    Views_count = Views.count()
    Views = make_page(Views, 1, 20)
    return render(request, 'views/index.html', {
        'Views': Views,
        'Views_count': Views_count,
        'Multiviews_count': Multiview.objects.count(),
    })


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Views = View.objects.filter()
    Views = make_page(Views, int(request.GET.get('page',1)), 20)
    return render(request, 'views/view-list.html', {
        'Views': Views,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    if request.method == 'POST':
        data = {}
        F = View_Form(request.POST)
        if F.is_valid():
            V = F.save()
            messages.success(request, _("View added with success."))
            data['response'] = 'ok'
            data['callback-url'] = V.get_absolute_url()
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'views/view.html', {
            'View_Form': View_Form(),
        })


@login_required()
@superuser_only()
def get(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    F = View_Form(instance=V)
    return render(request, 'views/view.html', {
        'View_Form': F,
    })


@login_required()
@superuser_only()
def update(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    F = View_Form(data=request.POST, instance=V)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("View updated with success."))
        data['response'] = 'ok'
        data['callback-url'] = V.get_absolute_url()
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, view_id):
    V = get_object_or_404(View.objects.filter(pk=view_id))
    V.delete()
    messages.success(request, _("View deleted with success."))
    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def add_sources(request):
    if request.method == 'POST':
        V = get_object_or_404(View.objects.filter(pk=request.POST['view_id']))
        V.sources.add(*request.POST.getlist('source_ids[]'))
        messages.success(request, _("Source(s) added with success."))
        return render_HTML_JSON(request, {}, 'base/messages.html', {})
    else:
        return render(request, 'modals/add_sources.html', {
          'views': View.objects.all(),
          'sources': Data_Source.objects.filter(pk__in=request.GET.getlist('ids[]'))
        })

# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several views in one request."""
    views = View.objects.filter(pk__in=request.POST.getlist('ids[]'))
    views.delete()
    messages.success(request, _("View(s) deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
