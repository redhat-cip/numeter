from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.forms import User_Form


@login_required()
def configuration_index(request):
    return render(request, 'configuration/index.html', {
        'title': 'Numeter - Configuration',
        'Form': User_Form(instance=request.user)
    })


@login_required()
def configuration_profile(request):
    return render(request, 'configuration/index.html', {
        'Form': User_Form(instance=request.user)
    })
