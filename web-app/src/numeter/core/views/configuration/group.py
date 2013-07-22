from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from core.models import Group
from core.forms import Group_Form
from core.utils.decorators import login_required, superuser_only
from core.utils import make_page


@login_required()
@superuser_only()
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
@superuser_only()
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
@superuser_only()
def group_get(request, group_id):
    G = get_object_or_404(Group.objects.filter(pk=group_id))
    F = Group_Form(instance=G)
    return render(request, 'configuration/users/group.html', {
        'Group_Form': F,
    })


@login_required()
@superuser_only()
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
@superuser_only()
def group_delete(request, group_id):
    G = get_object_or_404(Group.objects.filter(pk=group_id))
    G.delete()
    messages.success(request, _("Group deleted with success."))
    return render(request, 'base/messages.html', {})
