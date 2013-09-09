from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required
from core.utils import make_page
from multiviews.models import Event
from multiviews.forms.event import Small_Event_Form as Event_Form
from json import dumps as jdumps


@login_required()
def index(request):
    q = request.GET.get('q','')
    events = Event.objects.user_web_filter(q, request.user)
    events = make_page(events, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/event/index.html', {
        'Events': events,
        'q':q,
    })


@login_required()
def list(request):
    q = request.GET.get('q','')
    events = Event.objects.user_web_filter(q, request.user)
    events = make_page(events, int(request.GET.get('page',1)), 10)
    return render(request, 'customize/event/list.html', {
        'Events': events,
        'q':q,
    })


@login_required()
def add(request):
    return render(request, 'customize/event/event.html', {
       'Event_Form': Event_Form(user=request.user),
    })


@login_required()
def edit(request, event_id):
    E = get_object_or_404(Event.objects.filter(id=event_id))
    F = Event_Form(instance=E, user=request.user)
    return render(request, 'customize/event/event.html', {
        'Event_Form': F,
    })
