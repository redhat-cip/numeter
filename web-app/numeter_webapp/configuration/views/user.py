from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.utils.http import render_HTML_JSON
from core.models import User, Group
from configuration.forms.user import User_CreationForm, User_Admin_EditForm


@login_required()
@superuser_only()
def add(request):
    """Return an empty User_Form. """
    return render(request, 'users/user.html', {
        'User_Form': User_CreationForm(),
    })


@login_required()
@superuser_only()
def get(request, user_id):
    """Return a filled User_Form. """
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(instance=U)
    return render(request, 'users/user.html', {
        'User_Form': F,
    })
