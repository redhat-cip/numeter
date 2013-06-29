from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group

from core.models import User, Storage
from core.forms import User_EditForm, User_Admin_EditForm
from core.utils.decorators import login_required


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
def update_profile(request, user_id):
    U = get_object_or_404(User.objects.get(pk=user_is))
    F = User_EditForm(data=request.POST, instance=U)
    if F.is_valid:
        F.save()
        message.warning(_("Profile updated with success."))
        return render(request, 'base/messages.html', {})

