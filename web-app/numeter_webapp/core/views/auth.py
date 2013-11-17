from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as log_in, logout as log_out
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from core.utils.decorators import login_required

def login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                log_in(request, user)
                return redirect(request.POST.get('next','/'))
            else:
                messages.add_message(request, messages.ERROR, _(u"Incorrect login name or password !"))
        else:
            messages.add_message(request, messages.ERROR, _(u"Incorrect login name or password !"))
    return render(request, 'login.html', {})


@login_required()
def logout(request):
    log_out(request)
    return redirect('login')
