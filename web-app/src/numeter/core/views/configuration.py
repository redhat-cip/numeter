from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.models import User, Host, Storage, Group
from core.forms import User_EditForm, User_Admin_EditForm, User_PasswordForm, Storage_Form, User_CreationForm, Group_Form
from core.utils.decorators import login_required
from core.utils import make_page


@login_required()
def configuration_index(request):
    return render(request, 'configuration/index.html', {
        'title': 'Numeter - Configuration',
        'EditForm': User_EditForm(instance=request.user),
        'PasswordForm': User_PasswordForm(instance=request.user),
        'Users': User.objects.all(),
        'Groups': Group.objects.all(),
        'Storages': Storage.objects.all(),
    })


@login_required()
def profile_index(request):
    return render(request, 'configuration/profile.html', {
        'EditForm': User_EditForm(instance=request.user),
        'PasswordForm': User_PasswordForm(instance=request.user),
    })


@login_required()
def update_profile(request, user_id):
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
def update_password(request, user_id):
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


@login_required()
def user_index(request):
    return render(request, 'configuration/users/index.html', {
        'Users': User.objects.all_simpleuser(),
        'Superusers': User.objects.all_superuser(),
        'Groups': Group.objects.all(),
    })


@login_required()
def user_list(request):
    Users = User.objects.all_simpleuser()
    q = request.GET.get('q','')
    if q:
        Users = Users.filter(username__icontains=request.GET.get('q',''))
    Users = make_page(Users, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/users/user-list.html', {
        'Users': Users,
        'q':q,
    })


@login_required()
def superuser_list(request):
    Users = User.objects.all_superuser()
    q = request.GET.get('q','')
    if q:
        Users = Users.filter(username__icontains=request.GET.get('q',''))
    Users = make_page(Users, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/users/user-list.html', {
        'Users': Users,
        'q':q,
    })


@login_required()
def user_add(request):
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
        return render(request, 'configuration/users/user.html', {
            'User_Form': User_CreationForm(),
        })


@login_required()
def user_get(request, user_id):
    U = get_object_or_404(User.objects.filter(pk=user_id))
    F = User_Admin_EditForm(instance=U)
    return render(request, 'configuration/users/user.html', {
        'User_Form': F,
    })


@login_required()
def user_update(request, user_id):
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
def user_delete(request, user_id):
    U = get_object_or_404(User.objects.filter(pk=user_id))
    U.delete()
    messages.success(request, _("User deleted with success."))
    return render(request, 'base/messages.html', {})


@login_required()
def group_list(request):
    Groups = Group.objects.all()
    q = request.GET.get('q','')
    if q:
        Groups = Groups.filter(name__icontains=request.GET.get('q',''))
    Groups = make_page(Groups, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/users/group-list.html', {
        'Groups': Groups,
        'q':q,
    })


@login_required()
def group_add(request):
    if request.method == 'POST':
        F = Group_Form(request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("Group added with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})
    else:
        return render(request, 'configuration/users/group.html', {
            'Group_Form': Group_Form(),
        })


@login_required()
def group_get(request, group_id):
    G = get_object_or_404(Group.objects.filter(pk=group_id))
    F = Group_Form(instance=G)
    return render(request, 'configuration/users/group.html', {
        'Group_Form': F,
    })


@login_required()
def group_update(request, group_id):
    U = get_object_or_404(Group.objects.filter(pk=group_id))
    F = Group_Form(data=request.POST, instance=U)
    if F.is_valid():
        F.save()
        messages.success(request, _("Group updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))
    return render(request, 'base/messages.html', {})


@login_required()
def group_delete(request, group_id):
    G = get_object_or_404(Group.objects.filter(pk=group_id))
    G.delete()
    messages.success(request, _("Group deleted with success."))
    return render(request, 'base/messages.html', {})


@login_required()
def storage_index(request):
    Storages = Storage.objects.all()
    Storages_count = Storages.count()
    Storages = make_page(Storages, 1, 20)
    return render(request, 'configuration/storages/index.html', {
        'Storages': Storages,
        'Storages_count': Storages_count,
        'Hosts_count': Host.objects.count()
    })


@login_required()
def storage_list(request):
    Storages = Storage.objects.all()
    q = request.GET.get('q','')
    if q:
        Storages = Storages.filter(name__icontains=request.GET.get('q',''))
    Storages = make_page(Storages, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/storages/storage-list.html', {
        'Storages': Storages,
        'q':q,
    })


@login_required()
def storage_get(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    F = Storage_Form(instance=S)
    return render(request, 'configuration/storages/storage.html', {
        'Storage_Form': F,
    })


@login_required()
def storage_add(request):
    if request.method == 'POST':
        F = Storage_Form(request.POST)
        if F.is_valid():
            F.save()
            messages.success(request, _("Storage added with success."))
        else:
            for field,error in F.errors.items():
                messages.error(request, '<b>%s</b>: %s' % (field,error))
        return render(request, 'base/messages.html', {})
    else:
        return render(request, 'configuration/storages/storage.html', {
            'Storage_Form': Storage_Form(),
        })


@login_required()
def storage_update(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    F = Storage_Form(data=request.POST, instance=S)
    if F.is_valid():
        F.save()
        messages.success(request, _("Storage updated with success."))
    else:
        for field,error in F.errors.items():
            messages.error(request, '<b>%s</b>: %s' % (field,error))

    return render(request, 'base/messages.html', {})


@login_required()
def storage_delete(request, storage_id):
    S = get_object_or_404(Storage.objects.filter(pk=storage_id))
    S.delete()
    messages.success(request, _("Storage deleted with success."))
    return render(request, 'base/messages.html', {})


@login_required()
def host_list(request):
    Hosts = Host.objects.all()
    q = request.GET.get('q','')
    if q:
        Hosts = Hosts.filter(name__icontains=request.GET.get('q',''))
    Hosts = make_page(Hosts, int(request.GET.get('page',1)), 20)
    return render(request, 'configuration/storages/host-list.html', {
        'Hosts': Hosts,
        'q':q,
    })
