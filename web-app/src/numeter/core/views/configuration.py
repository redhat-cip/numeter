from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from core.models import User, Storage
from core.forms import User_EditForm, User_Admin_EditForm


@login_required()
def configuration_index(request):
    return render(request, 'configuration/index.html', {
        'title': 'Numeter - Configuration',
        'EditForm': User_EditForm(instance=request.user),
        'Users': User.objects.all(),
        'Groups': Group.objects.all(),
        'Storages': Storage.objects.all(),
    })


@login_required()
def configuration_profile(request):
    return render(request, 'configuration/index.html', {
        'EditForm': User_EditForm(instance=request.user)
    })


@login_required()
def update_profile(request):
	F = User_Form

