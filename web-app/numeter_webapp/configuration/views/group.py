from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Group
from configuration.forms.group import Group_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON


@login_required()
@superuser_only()
def list(request):
    groups = Group.objects.all()
    q = request.GET.get('q', '')
    if q:
        groups = groups.filter(name__icontains=request.GET.get('q',''))
    groups = make_page(groups, int(request.GET.get('page', 1)), 20)
    return render(request, 'users/group-list.html', {
        'Groups': Groups,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    return render(request, 'users/group.html', {
        'Group_Form': Group_Form(),
    })


@login_required()
@superuser_only()
def get(request, group_id):
    G = get_object_or_404(Group.objects.filter(pk=group_id))
    F = Group_Form(instance=G)
    return render(request, 'users/group.html', {
        'Group_Form': F,
    })
