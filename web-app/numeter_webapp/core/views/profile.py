from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import User
from core.utils.decorators import login_required
from configuration.forms.user import User_EditForm, User_PasswordForm


@login_required()
def modal(request):
    """Get profile modal."""
    return render(request, 'modals/profile.html', {
        'EditForm': User_EditForm(instance=request.user),
        'PasswordForm': User_PasswordForm(instance=request.user),
    })


@login_required()
def update(request, user_id):
    """Update profile."""
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_EditForm(data=request.POST, instance=U)
    if F.is_valid():
        F.save()
        messages.success(request, _("Profile updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
def password(request, user_id):
    """Change password."""
    if request.user.id != int(user_id):
        if not request.user.is_superuser:
            raise Http404

    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_PasswordForm(data=request.POST, instance=U)
    if F.is_valid():
        F.save()
        messages.success(request, _("Password updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})
