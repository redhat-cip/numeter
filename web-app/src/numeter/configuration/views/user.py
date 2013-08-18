from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.utils.decorators import login_required, superuser_only
from core.utils import make_page
from core.models import User, Group
from core.forms import User_CreationForm, User_Admin_EditForm


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
    if request.method == 'POST':
        F = User_CreationForm(request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("User added with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})
    else:
        return render(request, 'users/user.html', {
            'User_Form': User_CreationForm(),
        })


@login_required()
@superuser_only()
def get(request, user_id):
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(instance=U)
    return render(request, 'users/user.html', {
        'User_Form': F,
    })


@login_required()
@superuser_only()
def update(request, user_id):
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(data=request.POST, instance=U)
    if F.is_valid():
        F.save()
        messages.success(request, _("User updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
    return render(request, 'base/messages.html', {})


@login_required()
@superuser_only()
def delete(request, user_id):
    U = get_object_or_404(User.objects.filter(pk=user_id))
    U.delete()
    messages.success(request, _("User deleted with success."))
    return render(request, 'base/messages.html', {})
