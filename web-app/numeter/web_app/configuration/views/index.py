from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required
from configuration.forms.user import User_EditForm, User_PasswordForm


@login_required()
def index(request):
    return render(request, 'configuration_index.html', {
        'title': 'Numeter - Configuration',
        'EditForm': User_EditForm(instance=request.user),
        'PasswordForm': User_PasswordForm(instance=request.user),
    })

