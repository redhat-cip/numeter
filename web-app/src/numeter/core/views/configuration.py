from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def configuration_index(request):
	return render(request, 'settings.html', {})
