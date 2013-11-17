from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import requires_csrf_token

from core.utils.decorators import login_required, superuser_only
from core.models import User, Group
from configuration.forms.user import User_EditForm, User_PasswordForm


@login_required()
@superuser_only()
@requires_csrf_token
def index(request):
    """Configuration index."""
    return render(request, 'configuration_index.html', {
        'title': 'Numeter - Configuration',
        'Users': User.objects.all_simpleuser(),
        'Superusers': User.objects.all_superuser(),
        'Groups': Group.objects.all(),
    })

