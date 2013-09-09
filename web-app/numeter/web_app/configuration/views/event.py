from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from multiviews.models import Event
from configuration.forms.event import Event_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def list(request):
    q = request.GET.get('q','')
    Events = Event.objects.web_filter(q)
    Events = make_page(Events, int(request.GET.get('page',1)), 20)
    return render(request, 'views/event-list.html', {
        'Events': Events,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    if request.method == 'POST':
        data = {}
        F = Event_Form(request.POST)
        if F.is_valid():
            E = F.save()
            messages.success(request, _("Event added with success."))
            data.update({
              'response': 'ok',
              'callback-url': E.get_absolute_url(),
              'id':E.pk,
            })
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'views/event.html', {
            'Event_Form': Event_Form(),
        })


@login_required()
@superuser_only()
def get(request, event_id):
    S = get_object_or_404(Event.objects.filter(pk=event_id))
    F = Event_Form(instance=S)
    return render(request, 'views/event.html', {
        'Event_Form': F,
    })


@login_required()
@superuser_only()
def update(request, event_id):
    S = get_object_or_404(Event.objects.filter(pk=event_id))
    F = Event_Form(data=request.POST, instance=S)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("Event updated with success."))
        data['response'] = 'ok'
        data['callback-url'] = S.get_absolute_url()
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, event_id):
    S = get_object_or_404(Event.objects.filter(pk=event_id))
    S.delete()
    messages.success(request, _("Event deleted with success."))
    return render(request, 'base/messages.html', {})


# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several events in one request."""
    events = Event.objects.filter(pk__in=request.POST.getlist('ids[]'))
    events.delete()
    messages.success(request, _("Event(s) deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
