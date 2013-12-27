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
def index(request):
    """Users and groups index."""
    return render(request, 'users/index.html', {
        'Users': User.objects.all_simpleuser(),
        'Superusers': User.objects.all_superuser(),
        'Groups': Group.objects.all(),
    })


@login_required()
@superuser_only()
def user_list(request):
    """List users and filter by request."""
    q = request.GET.get('q','')
    Users = User.objects.web_filter(q).filter(is_superuser=False)
    Users = make_page(Users, int(request.GET.get('page',1)), 20)
    return render(request, 'users/user-list.html', {
        'Users': Users,
        'q':q,
    })


@login_required()
@superuser_only()
def superuser_list(request):
    """List superusers and filter by request."""
    q = request.GET.get('q','')
    Users = User.objects.web_filter(q).filter(is_superuser=True)
    Users = make_page(Users, int(request.GET.get('page',1)), 20)
    return render(request, 'users/user-list.html', {
        'Users': Users,
        'q':q,
    })


@login_required()
@superuser_only()
def add(request):
    """
    GET: User Form.
    POST: Create user.
    """
    if request.method == 'POST':
        F = User_CreationForm(request.POST)
        data = {}
        if F.is_valid():
            U = F.save()
            messages.success(request, _("User added with success."))
            data['response'] = 'ok'
            data['callback-url'] = U.get_absolute_url()
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
            data['response'] = 'error'
        return render_HTML_JSON(request, data, 'base/messages.html', {})
    else:
        return render(request, 'users/user.html', {
            'User_Form': User_CreationForm(),
        })


@login_required()
@superuser_only()
def get(request, user_id):
    """Get a user."""
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(instance=U)
    return render(request, 'users/user.html', {
        'User_Form': F,
    })


@login_required()
@superuser_only()
def update(request, user_id):
    """Update a user."""
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(data=request.POST, instance=U)
    data = {}
    if F.is_valid():
        F.save()
        messages.success(request, _("User updated with success."))
        data['response'] = 'ok'
        data['callback-url'] = U.get_absolute_url()
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
        data['response'] = 'error'
    return render_HTML_JSON(request, data, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, user_id):
    """Delete a user."""
    U = get_object_or_404(User.objects.filter(pk=user_id))
    U.delete()
    messages.success(request, _("User deleted with success."))
    return render(request, 'base/messages.html', {})


# TODO : Make unittest
@login_required()
@superuser_only()
def bulk_delete(request):
    """Delete several users in one request."""
    users = User.objects.filter(pk__in=request.POST.getlist('ids[]'))
    users.delete()
    messages.success(request, _("User(s) deleted with success."))
    return render_HTML_JSON(request, {}, 'base/messages.html', {})
